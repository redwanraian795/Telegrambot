import json
import os
import random
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from ai_services import ai_services

class GamesService:
    """Interactive games, trivia, puzzles, and entertainment features"""
    
    def __init__(self):
        self.game_sessions = {}
        self.trivia_categories = [
            "science", "history", "geography", "sports", "entertainment", 
            "technology", "literature", "art", "music", "general"
        ]
        self.word_lists = self.load_word_lists()
        self.riddles_db = self.load_riddles()
    
    def load_word_lists(self) -> Dict[str, List[str]]:
        """Load word lists for word games"""
        return {
            "easy": ["cat", "dog", "sun", "moon", "tree", "house", "car", "book", "water", "fire"],
            "medium": ["computer", "elephant", "rainbow", "butterfly", "mountain", "chocolate", "telephone", "keyboard"],
            "hard": ["sophisticated", "metamorphosis", "phenomenon", "extraordinary", "philosophical", "revolutionary"]
        }
    
    def load_riddles(self) -> List[Dict[str, str]]:
        """Load riddles database"""
        return [
            {"riddle": "I have cities, but no houses. I have mountains, but no trees. I have water, but no fish. What am I?", "answer": "map"},
            {"riddle": "The more you take, the more you leave behind. What am I?", "answer": "footsteps"},
            {"riddle": "I'm tall when I'm young, and short when I'm old. What am I?", "answer": "candle"},
            {"riddle": "What has keys but no locks, space but no room, and you can enter but not go inside?", "answer": "keyboard"},
            {"riddle": "I have branches, but no fruit, trunk, or leaves. What am I?", "answer": "bank"},
            {"riddle": "What gets wet while drying?", "answer": "towel"},
            {"riddle": "I'm not alive, but I grow. I don't have lungs, but I need air. What am I?", "answer": "fire"},
            {"riddle": "What has a head and a tail but no body?", "answer": "coin"}
        ]
    
    def start_trivia_game(self, user_id: str, category: str = "general", difficulty: str = "medium") -> Dict[str, Any]:
        """Start a trivia game session"""
        try:
            if category not in self.trivia_categories:
                category = "general"
            
            # Generate trivia questions using AI
            trivia_prompt = f"""Generate 5 {difficulty} difficulty trivia questions about {category}. 

Format each question as:
Q1: [Question text]
A: [Correct answer]
B: [Wrong answer]
C: [Wrong answer]
D: [Wrong answer]
Correct: A

Make questions engaging and educational. Ensure one clear correct answer."""
            
            trivia_content = ai_services.chat_with_ai(trivia_prompt, "trivia_generation")
            
            # Parse questions
            questions = self._parse_trivia_questions(trivia_content)
            
            # Create game session
            game_id = f"trivia_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.game_sessions[game_id] = {
                'type': 'trivia',
                'user_id': user_id,
                'category': category,
                'difficulty': difficulty,
                'questions': questions,
                'current_question': 0,
                'score': 0,
                'start_time': datetime.now().isoformat(),
                'status': 'active'
            }
            
            # Return first question
            if questions:
                first_question = questions[0]
                return {
                    'game_id': game_id,
                    'question_number': 1,
                    'total_questions': len(questions),
                    'question': first_question['question'],
                    'options': first_question['options'],
                    'category': category,
                    'difficulty': difficulty
                }
            else:
                return {"error": "Failed to generate trivia questions"}
                
        except Exception as e:
            return {"error": f"Trivia game creation failed: {str(e)}"}
    
    def _parse_trivia_questions(self, content: str) -> List[Dict[str, Any]]:
        """Parse AI-generated trivia content into structured questions"""
        questions = []
        lines = content.split('\n')
        current_question = {}
        
        for line in lines:
            line = line.strip()
            if line.startswith('Q') and ':' in line:
                if current_question:
                    questions.append(current_question)
                current_question = {'question': line.split(':', 1)[1].strip(), 'options': {}, 'correct': ''}
            elif line.startswith(('A:', 'B:', 'C:', 'D:')):
                option_key = line[0]
                option_text = line.split(':', 1)[1].strip()
                current_question['options'][option_key] = option_text
            elif line.startswith('Correct:'):
                current_question['correct'] = line.split(':', 1)[1].strip()
        
        if current_question:
            questions.append(current_question)
        
        return questions
    
    def generate_trivia(self, user_id: str, category: str = "general") -> Dict[str, Any]:
        """Generate trivia questions for user (public method)"""
        return self.start_trivia_game(user_id, category)
    
    def generate_trivia_question(self, category: str = "general") -> Dict[str, Any]:
        """Generate a single trivia question"""
        try:
            trivia_prompt = f"""Generate 1 {category} trivia question.

Format:
Q: [question text]
A: [option A]
B: [option B] 
C: [option C]
D: [option D]
Correct: [A/B/C/D]

Make it engaging and educational."""

            content = ai_services.chat_with_ai(trivia_prompt, "trivia_generation")
            questions = self._parse_trivia_questions(content)
            
            if questions:
                return {
                    'success': True,
                    'question': questions[0]['question'],
                    'options': questions[0]['options'],
                    'correct': questions[0]['correct'],
                    'category': category
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to generate trivia question'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Trivia generation failed: {str(e)}'
            }
    
    def answer_trivia_question(self, game_id: str, user_answer: str) -> Dict[str, Any]:
        """Process trivia answer and return next question or results"""
        try:
            if game_id not in self.game_sessions:
                return {"error": "Game session not found"}
            
            session = self.game_sessions[game_id]
            if session['status'] != 'active':
                return {"error": "Game session is not active"}
            
            current_q_index = session['current_question']
            if current_q_index >= len(session['questions']):
                return {"error": "No more questions available"}
            
            current_question = session['questions'][current_q_index]
            correct_answer = current_question['correct']
            is_correct = user_answer.upper() == correct_answer.upper()
            
            if is_correct:
                session['score'] += 1
            
            # Move to next question
            session['current_question'] += 1
            
            # Check if game is complete
            if session['current_question'] >= len(session['questions']):
                session['status'] = 'completed'
                session['end_time'] = datetime.now().isoformat()
                
                return {
                    'game_complete': True,
                    'final_score': session['score'],
                    'total_questions': len(session['questions']),
                    'percentage': round((session['score'] / len(session['questions'])) * 100, 1),
                    'correct_answer': correct_answer,
                    'is_correct': is_correct,
                    'category': session['category'],
                    'difficulty': session['difficulty']
                }
            else:
                # Return next question
                next_question = session['questions'][session['current_question']]
                return {
                    'game_complete': False,
                    'question_number': session['current_question'] + 1,
                    'total_questions': len(session['questions']),
                    'question': next_question['question'],
                    'options': next_question['options'],
                    'correct_answer': correct_answer,
                    'is_correct': is_correct,
                    'current_score': session['score']
                }
                
        except Exception as e:
            return {"error": f"Answer processing failed: {str(e)}"}
    
    def create_word_game(self, user_id: str, game_type: str = "word_association") -> Dict[str, Any]:
        """Create various word games - alias for start_word_game"""
        return self.start_word_game(user_id, game_type)
    
    def start_word_game(self, user_id: str, game_type: str = "word_association") -> Dict[str, Any]:
        """Start various word games"""
        try:
            game_types = {
                "word_association": self._start_word_association,
                "word_scramble": self._start_word_scramble,
                "rhyme_time": self._start_rhyme_game,
                "story_builder": self._start_story_builder
            }
            
            if game_type not in game_types:
                game_type = "word_association"
            
            return game_types[game_type](user_id)
            
        except Exception as e:
            return {"error": f"Word game creation failed: {str(e)}"}
    
    def _start_word_association(self, user_id: str) -> Dict[str, Any]:
        """Start word association game"""
        starting_words = ["ocean", "mountain", "music", "adventure", "mystery", "rainbow", "friendship", "journey"]
        starting_word = random.choice(starting_words)
        
        game_id = f"word_assoc_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.game_sessions[game_id] = {
            'type': 'word_association',
            'user_id': user_id,
            'words_chain': [starting_word],
            'start_time': datetime.now().isoformat(),
            'status': 'active',
            'turn_count': 0
        }
        
        return {
            'game_id': game_id,
            'game_type': 'word_association',
            'starting_word': starting_word,
            'instructions': 'Say a word that relates to the previous word. Keep the chain going!',
            'turn': 1
        }
    
    def _start_word_scramble(self, user_id: str) -> Dict[str, Any]:
        """Start word scramble game"""
        difficulty = random.choice(["easy", "medium", "hard"])
        word = random.choice(self.word_lists[difficulty])
        scrambled = ''.join(random.sample(word, len(word)))
        
        game_id = f"word_scramble_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.game_sessions[game_id] = {
            'type': 'word_scramble',
            'user_id': user_id,
            'original_word': word,
            'scrambled_word': scrambled,
            'difficulty': difficulty,
            'start_time': datetime.now().isoformat(),
            'status': 'active',
            'attempts': 0
        }
        
        return {
            'game_id': game_id,
            'game_type': 'word_scramble',
            'scrambled_word': scrambled,
            'difficulty': difficulty,
            'word_length': len(word),
            'instructions': 'Unscramble this word!'
        }
    
    def _start_rhyme_game(self, user_id: str) -> Dict[str, Any]:
        """Start rhyming game"""
        rhyme_words = ["cat", "run", "light", "tree", "star", "blue", "sing", "dance"]
        target_word = random.choice(rhyme_words)
        
        game_id = f"rhyme_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.game_sessions[game_id] = {
            'type': 'rhyme_time',
            'user_id': user_id,
            'target_word': target_word,
            'found_rhymes': [],
            'start_time': datetime.now().isoformat(),
            'status': 'active'
        }
        
        return {
            'game_id': game_id,
            'game_type': 'rhyme_time',
            'target_word': target_word,
            'instructions': f'Find words that rhyme with "{target_word}"! Send one word at a time.',
            'found_count': 0
        }
    
    def _start_story_builder(self, user_id: str) -> Dict[str, Any]:
        """Start collaborative story building"""
        story_starters = [
            "Once upon a time in a magical forest...",
            "The spaceship landed on the mysterious planet...",
            "Detective Johnson discovered a strange clue...",
            "The old lighthouse keeper noticed something unusual...",
            "In the year 2150, humanity made first contact..."
        ]
        
        starter = random.choice(story_starters)
        
        game_id = f"story_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.game_sessions[game_id] = {
            'type': 'story_builder',
            'user_id': user_id,
            'story_parts': [starter],
            'start_time': datetime.now().isoformat(),
            'status': 'active',
            'turn_count': 1
        }
        
        return {
            'game_id': game_id,
            'game_type': 'story_builder',
            'story_start': starter,
            'instructions': 'Continue the story! Add 1-2 sentences to keep it going.',
            'turn': 1
        }
    
    def start_story_building(self, user_id: str) -> Dict[str, Any]:
        """Start collaborative story building - alias for _start_story_builder"""
        return self._start_story_builder(user_id)
    
    def play_word_game(self, game_id: str, user_input: str) -> Dict[str, Any]:
        """Process word game input"""
        try:
            if game_id not in self.game_sessions:
                return {"error": "Game session not found"}
            
            session = self.game_sessions[game_id]
            game_type = session['type']
            
            if game_type == "word_association":
                return self._play_word_association(session, user_input)
            elif game_type == "word_scramble":
                return self._play_word_scramble(session, user_input)
            elif game_type == "rhyme_time":
                return self._play_rhyme_game(session, user_input)
            elif game_type == "story_builder":
                return self._play_story_builder(session, user_input)
            else:
                return {"error": "Unknown game type"}
                
        except Exception as e:
            return {"error": f"Game play failed: {str(e)}"}
    
    def _play_word_association(self, session: Dict, user_input: str) -> Dict[str, Any]:
        """Process word association turn"""
        last_word = session['words_chain'][-1]
        user_word = user_input.strip().lower()
        
        # Use AI to validate association
        validation_prompt = f"Are '{last_word}' and '{user_word}' reasonably associated? Consider themes, categories, sounds, meanings, or logical connections. Answer with just 'yes' or 'no' and briefly explain why."
        
        validation = ai_services.chat_with_ai(validation_prompt, "word_association")
        is_valid = "yes" in validation.lower()
        
        if is_valid:
            session['words_chain'].append(user_word)
            session['turn_count'] += 1
            
            # AI responds with next word
            ai_prompt = f"Given this word chain: {' -> '.join(session['words_chain'])}, what word would you associate with '{user_word}'? Give just one word that connects naturally."
            
            ai_word = ai_services.chat_with_ai(ai_prompt, "word_association").strip().lower()
            # Clean AI response to get just the word
            ai_word = ai_word.split()[0] if ai_word.split() else "continue"
            
            session['words_chain'].append(ai_word)
            session['turn_count'] += 1
            
            return {
                'valid': True,
                'your_word': user_word,
                'ai_word': ai_word,
                'chain_length': len(session['words_chain']),
                'full_chain': ' -> '.join(session['words_chain']),
                'turn': session['turn_count']
            }
        else:
            return {
                'valid': False,
                'reason': validation,
                'last_word': last_word,
                'your_word': user_word,
                'try_again': True
            }
    
    def _play_word_scramble(self, session: Dict, user_input: str) -> Dict[str, Any]:
        """Process word scramble guess"""
        session['attempts'] += 1
        correct_word = session['original_word']
        user_guess = user_input.strip().lower()
        
        if user_guess == correct_word:
            session['status'] = 'completed'
            return {
                'correct': True,
                'word': correct_word,
                'attempts': session['attempts'],
                'difficulty': session['difficulty'],
                'congratulations': f"Excellent! You solved '{correct_word}' in {session['attempts']} attempts!"
            }
        else:
            hint = ""
            if session['attempts'] >= 3:
                hint = f"Hint: The word starts with '{correct_word[0]}'"
            elif session['attempts'] >= 5:
                hint = f"Hint: The word is '{correct_word[:2]}___'"
            
            return {
                'correct': False,
                'guess': user_guess,
                'attempts': session['attempts'],
                'hint': hint,
                'scrambled_word': session['scrambled_word'],
                'try_again': True
            }
    
    def _play_rhyme_game(self, session: Dict, user_input: str) -> Dict[str, Any]:
        """Process rhyme game input"""
        target_word = session['target_word']
        user_word = user_input.strip().lower()
        
        # Check if already found
        if user_word in session['found_rhymes']:
            return {
                'already_found': True,
                'word': user_word,
                'found_rhymes': session['found_rhymes'],
                'count': len(session['found_rhymes'])
            }
        
        # Use AI to validate rhyme
        rhyme_prompt = f"Does '{user_word}' rhyme with '{target_word}'? Consider perfect rhymes, near rhymes, and slant rhymes. Answer 'yes' or 'no' and explain."
        
        validation = ai_services.chat_with_ai(rhyme_prompt, "rhyme_validation")
        is_rhyme = "yes" in validation.lower()
        
        if is_rhyme:
            session['found_rhymes'].append(user_word)
            return {
                'valid_rhyme': True,
                'word': user_word,
                'target': target_word,
                'found_rhymes': session['found_rhymes'],
                'count': len(session['found_rhymes']),
                'encouragement': f"Great rhyme! '{user_word}' rhymes with '{target_word}'"
            }
        else:
            return {
                'valid_rhyme': False,
                'word': user_word,
                'target': target_word,
                'reason': validation,
                'try_again': True
            }
    
    def _play_story_builder(self, session: Dict, user_input: str) -> Dict[str, Any]:
        """Process story building turn"""
        user_addition = user_input.strip()
        session['story_parts'].append(f"[You]: {user_addition}")
        session['turn_count'] += 1
        
        # AI continues the story
        current_story = " ".join(session['story_parts'])
        ai_prompt = f"Continue this collaborative story with 1-2 sentences that build on what came before: {current_story}"
        
        ai_addition = ai_services.chat_with_ai(ai_prompt, "story_continuation")
        session['story_parts'].append(f"[AI]: {ai_addition}")
        session['turn_count'] += 1
        
        return {
            'your_addition': user_addition,
            'ai_addition': ai_addition,
            'story_so_far': " ".join(session['story_parts']),
            'turn': session['turn_count'],
            'continue': True
        }
    
    def get_random_riddle(self) -> Dict[str, Any]:
        """Get a random riddle"""
        riddle = random.choice(self.riddles_db)
        return {
            'riddle': riddle['riddle'],
            'riddle_id': self.riddles_db.index(riddle),
            'instructions': 'Think carefully and send your answer!'
        }
    
    def check_riddle_answer(self, riddle_id: int, user_answer: str) -> Dict[str, Any]:
        """Check riddle answer"""
        try:
            if riddle_id >= len(self.riddles_db):
                return {"error": "Invalid riddle ID"}
            
            riddle = self.riddles_db[riddle_id]
            correct_answer = riddle['answer'].lower()
            user_answer_clean = user_answer.strip().lower()
            
            is_correct = user_answer_clean == correct_answer
            
            if is_correct:
                return {
                    'correct': True,
                    'answer': correct_answer,
                    'congratulations': 'Excellent! You solved the riddle!',
                    'riddle': riddle['riddle']
                }
            else:
                # Give hint for close answers
                hint = ""
                if len(user_answer_clean) == len(correct_answer):
                    hint = f"Hint: The answer starts with '{correct_answer[0]}'"
                
                return {
                    'correct': False,
                    'your_answer': user_answer,
                    'hint': hint,
                    'riddle': riddle['riddle'],
                    'try_again': True
                }
                
        except Exception as e:
            return {"error": f"Riddle checking failed: {str(e)}"}
    
    def get_game_stats(self, user_id: str) -> Dict[str, Any]:
        """Get user's game statistics"""
        user_games = [game for game in self.game_sessions.values() if game['user_id'] == user_id]
        
        stats = {
            'total_games': len(user_games),
            'games_by_type': {},
            'completed_games': 0,
            'trivia_stats': {'total': 0, 'avg_score': 0},
            'word_game_stats': {'total': 0, 'types_played': set()},
            'recent_games': []
        }
        
        for game in user_games:
            game_type = game['type']
            stats['games_by_type'][game_type] = stats['games_by_type'].get(game_type, 0) + 1
            
            if game['status'] == 'completed':
                stats['completed_games'] += 1
            
            if game_type == 'trivia' and game['status'] == 'completed':
                stats['trivia_stats']['total'] += 1
                # Would calculate average score here
            
            if 'word' in game_type:
                stats['word_game_stats']['total'] += 1
                stats['word_game_stats']['types_played'].add(game_type)
            
            # Add to recent games (last 5)
            if len(stats['recent_games']) < 5:
                stats['recent_games'].append({
                    'type': game_type,
                    'status': game['status'],
                    'start_time': game['start_time']
                })
        
        stats['word_game_stats']['types_played'] = list(stats['word_game_stats']['types_played'])
        
        return stats

# Global instance
games_service = GamesService()