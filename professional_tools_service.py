import json
import os
import csv
import base64
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from ai_services import ai_services
from io import StringIO, BytesIO

class ProfessionalToolsService:
    """Professional tools for business, development, and productivity"""
    
    def __init__(self):
        self.templates = self.load_templates()
        self.code_languages = [
            'python', 'javascript', 'typescript', 'java', 'cpp', 'csharp', 
            'go', 'rust', 'php', 'ruby', 'swift', 'kotlin', 'html', 'css', 'sql'
        ]
        
    def load_templates(self) -> Dict[str, str]:
        """Load document templates"""
        return {
            'invoice': '''INVOICE

Company: {company_name}
Address: {company_address}
Date: {date}
Invoice #: {invoice_number}

Bill To:
{client_name}
{client_address}

Items:
{items}

Subtotal: ${subtotal}
Tax ({tax_rate}%): ${tax_amount}
Total: ${total}

Payment Terms: {payment_terms}
Due Date: {due_date}''',
            
            'meeting_minutes': '''MEETING MINUTES

Meeting: {meeting_title}
Date: {date}
Time: {time}
Attendees: {attendees}

AGENDA:
{agenda}

DISCUSSION:
{discussion}

ACTION ITEMS:
{action_items}

NEXT MEETING: {next_meeting}''',
            
            'project_proposal': '''PROJECT PROPOSAL

Title: {project_title}
Date: {date}
Prepared for: {client}
Prepared by: {company}

EXECUTIVE SUMMARY:
{summary}

PROJECT SCOPE:
{scope}

TIMELINE:
{timeline}

BUDGET:
{budget}

DELIVERABLES:
{deliverables}

TERMS & CONDITIONS:
{terms}''',
            
            'resume': '''RESUME

{full_name}
{contact_info}

OBJECTIVE:
{objective}

EXPERIENCE:
{experience}

EDUCATION:
{education}

SKILLS:
{skills}

CERTIFICATIONS:
{certifications}

REFERENCES:
Available upon request'''
        }
    
    def generate_invoice(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate professional invoice"""
        try:
            # Calculate totals
            items = invoice_data.get('items', [])
            subtotal = sum(item.get('amount', 0) for item in items)
            tax_rate = invoice_data.get('tax_rate', 0)
            tax_amount = subtotal * (tax_rate / 100)
            total = subtotal + tax_amount
            
            # Format items
            items_text = ""
            for item in items:
                items_text += f"{item.get('description', '')}: ${item.get('amount', 0):.2f}\n"
            
            # Fill template
            invoice_content = self.templates['invoice'].format(
                company_name=invoice_data.get('company_name', ''),
                company_address=invoice_data.get('company_address', ''),
                date=invoice_data.get('date', datetime.now().strftime('%Y-%m-%d')),
                invoice_number=invoice_data.get('invoice_number', f"INV-{datetime.now().strftime('%Y%m%d-%H%M%S')}"),
                client_name=invoice_data.get('client_name', ''),
                client_address=invoice_data.get('client_address', ''),
                items=items_text,
                subtotal=f"{subtotal:.2f}",
                tax_rate=tax_rate,
                tax_amount=f"{tax_amount:.2f}",
                total=f"{total:.2f}",
                payment_terms=invoice_data.get('payment_terms', 'Net 30'),
                due_date=invoice_data.get('due_date', (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'))
            )
            
            # Save invoice
            filename = f"invoice_{invoice_data.get('invoice_number', datetime.now().strftime('%Y%m%d_%H%M%S'))}.txt"
            filepath = os.path.join("downloads", filename)
            os.makedirs("downloads", exist_ok=True)
            
            with open(filepath, 'w') as f:
                f.write(invoice_content)
            
            return {
                'success': True,
                'invoice_content': invoice_content,
                'filepath': filepath,
                'subtotal': subtotal,
                'tax_amount': tax_amount,
                'total': total
            }
            
        except Exception as e:
            return {"error": f"Invoice generation failed: {str(e)}"}
    
    def create_meeting_minutes(self, meeting_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate meeting minutes"""
        try:
            minutes_content = self.templates['meeting_minutes'].format(
                meeting_title=meeting_data.get('title', ''),
                date=meeting_data.get('date', datetime.now().strftime('%Y-%m-%d')),
                time=meeting_data.get('time', datetime.now().strftime('%H:%M')),
                attendees=', '.join(meeting_data.get('attendees', [])),
                agenda=meeting_data.get('agenda', ''),
                discussion=meeting_data.get('discussion', ''),
                action_items=meeting_data.get('action_items', ''),
                next_meeting=meeting_data.get('next_meeting', 'TBD')
            )
            
            filename = f"meeting_minutes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            filepath = os.path.join("downloads", filename)
            os.makedirs("downloads", exist_ok=True)
            
            with open(filepath, 'w') as f:
                f.write(minutes_content)
            
            return {
                'success': True,
                'minutes_content': minutes_content,
                'filepath': filepath
            }
            
        except Exception as e:
            return {"error": f"Meeting minutes creation failed: {str(e)}"}
    
    def generate_project_proposal(self, proposal_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate project proposal"""
        try:
            proposal_content = self.templates['project_proposal'].format(
                project_title=proposal_data.get('title', ''),
                date=datetime.now().strftime('%Y-%m-%d'),
                client=proposal_data.get('client', ''),
                company=proposal_data.get('company', ''),
                summary=proposal_data.get('summary', ''),
                scope=proposal_data.get('scope', ''),
                timeline=proposal_data.get('timeline', ''),
                budget=proposal_data.get('budget', ''),
                deliverables=proposal_data.get('deliverables', ''),
                terms=proposal_data.get('terms', '')
            )
            
            filename = f"proposal_{proposal_data.get('title', 'project').replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.txt"
            filepath = os.path.join("downloads", filename)
            os.makedirs("downloads", exist_ok=True)
            
            with open(filepath, 'w') as f:
                f.write(proposal_content)
            
            return {
                'success': True,
                'proposal_content': proposal_content,
                'filepath': filepath
            }
            
        except Exception as e:
            return {"error": f"Project proposal generation failed: {str(e)}"}
    
    def create_spreadsheet(self, data: List[List[str]], filename: str = None) -> Dict[str, Any]:
        """Create CSV spreadsheet"""
        try:
            if not filename:
                filename = f"spreadsheet_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            filepath = os.path.join("downloads", filename)
            os.makedirs("downloads", exist_ok=True)
            
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                for row in data:
                    writer.writerow(row)
            
            return {
                'success': True,
                'filepath': filepath,
                'rows': len(data),
                'columns': len(data[0]) if data else 0
            }
            
        except Exception as e:
            return {"error": f"Spreadsheet creation failed: {str(e)}"}
    
    def analyze_code(self, code: str, language: str) -> Dict[str, Any]:
        """Comprehensive code analysis"""
        try:
            analysis_prompt = f"""Analyze this {language} code comprehensively:

```{language}
{code}
```

Provide detailed analysis including:
1. Code quality assessment (1-10 scale)
2. Security vulnerabilities and concerns
3. Performance optimization opportunities
4. Code style and best practices compliance
5. Potential bugs or issues
6. Maintainability assessment
7. Documentation quality
8. Suggestions for improvement
9. Complexity analysis
10. Test coverage recommendations

Be thorough and professional in your analysis."""
            
            analysis = ai_services.chat_with_ai(analysis_prompt, "code_analysis")
            
            return {
                'success': True,
                'language': language,
                'code_length': len(code),
                'lines_of_code': len(code.split('\n')),
                'analysis': analysis,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Code analysis failed: {str(e)}"}
    
    def generate_documentation(self, code: str, language: str, doc_type: str = "api") -> Dict[str, Any]:
        """Generate code documentation"""
        try:
            doc_prompt = f"""Generate comprehensive {doc_type} documentation for this {language} code:

```{language}
{code}
```

Create professional documentation including:
1. Overview and purpose
2. Function/method descriptions
3. Parameter details with types
4. Return value descriptions
5. Usage examples
6. Error handling information
7. Dependencies and requirements
8. Installation/setup instructions (if applicable)
9. API endpoints (if applicable)
10. Code examples for common use cases

Format the documentation professionally with clear structure."""
            
            documentation = ai_services.chat_with_ai(doc_prompt, "documentation_generation")
            
            # Save documentation
            filename = f"documentation_{language}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            filepath = os.path.join("downloads", filename)
            os.makedirs("downloads", exist_ok=True)
            
            with open(filepath, 'w') as f:
                f.write(documentation)
            
            return {
                'success': True,
                'documentation': documentation,
                'filepath': filepath,
                'doc_type': doc_type,
                'language': language
            }
            
        except Exception as e:
            return {"error": f"Documentation generation failed: {str(e)}"}
    
    def create_test_cases(self, code: str, language: str, test_framework: str = "auto") -> Dict[str, Any]:
        """Generate test cases for code"""
        try:
            test_prompt = f"""Generate comprehensive test cases for this {language} code:

```{language}
{code}
```

Create test cases using appropriate {test_framework if test_framework != 'auto' else 'testing framework'} including:
1. Unit tests for all functions/methods
2. Integration tests where applicable
3. Edge case testing
4. Error condition testing
5. Performance testing scenarios
6. Mock data and fixtures
7. Setup and teardown procedures
8. Test data validation
9. Assertion examples
10. Coverage recommendations

Provide working, executable test code with proper imports and structure."""
            
            test_cases = ai_services.chat_with_ai(test_prompt, "test_generation")
            
            # Save test file
            test_extension = {
                'python': '.py',
                'javascript': '.test.js',
                'typescript': '.test.ts',
                'java': '.java',
                'csharp': '.cs'
            }.get(language, '.txt')
            
            filename = f"test_cases_{language}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{test_extension}"
            filepath = os.path.join("downloads", filename)
            os.makedirs("downloads", exist_ok=True)
            
            with open(filepath, 'w') as f:
                f.write(test_cases)
            
            return {
                'success': True,
                'test_cases': test_cases,
                'filepath': filepath,
                'language': language,
                'framework': test_framework
            }
            
        except Exception as e:
            return {"error": f"Test case generation failed: {str(e)}"}
    
    def optimize_code(self, code: str, language: str, optimization_type: str = "performance") -> Dict[str, Any]:
        """Optimize code for performance, readability, or security"""
        try:
            optimization_prompt = f"""Optimize this {language} code for {optimization_type}:

```{language}
{code}
```

Provide optimized version with:
1. Improved {optimization_type}
2. Detailed explanation of changes made
3. Before/after comparison
4. Performance impact analysis (if applicable)
5. Security improvements (if applicable)
6. Readability enhancements (if applicable)
7. Best practices implementation
8. Alternative approaches considered
9. Trade-offs and considerations
10. Recommendations for further optimization

Show both original and optimized code clearly marked."""
            
            optimization = ai_services.chat_with_ai(optimization_prompt, "code_optimization")
            
            return {
                'success': True,
                'original_code': code,
                'optimization_type': optimization_type,
                'optimized_result': optimization,
                'language': language,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Code optimization failed: {str(e)}"}
    
    def create_database_schema(self, requirements: str, database_type: str = "postgresql") -> Dict[str, Any]:
        """Generate database schema from requirements"""
        try:
            schema_prompt = f"""Create a comprehensive {database_type} database schema based on these requirements:

{requirements}

Provide:
1. Complete table definitions with appropriate data types
2. Primary and foreign key relationships
3. Indexes for performance optimization
4. Constraints and validations
5. Sample data insertion scripts
6. Query examples for common operations
7. Database normalization considerations
8. Performance optimization suggestions
9. Security considerations
10. Migration scripts (if applicable)

Generate production-ready SQL code with proper formatting."""
            
            schema = ai_services.chat_with_ai(schema_prompt, "database_schema")
            
            # Save schema file
            filename = f"database_schema_{database_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
            filepath = os.path.join("downloads", filename)
            os.makedirs("downloads", exist_ok=True)
            
            with open(filepath, 'w') as f:
                f.write(schema)
            
            return {
                'success': True,
                'schema': schema,
                'filepath': filepath,
                'database_type': database_type,
                'requirements': requirements
            }
            
        except Exception as e:
            return {"error": f"Database schema generation failed: {str(e)}"}
    
    def analyze_business_data(self, data: List[Dict], analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """Analyze business data and provide insights"""
        try:
            # Convert data to readable format
            data_summary = f"Dataset contains {len(data)} records with fields: {list(data[0].keys()) if data else 'No data'}"
            
            # Sample data for analysis (first 5 records)
            sample_data = data[:5] if len(data) > 5 else data
            
            analysis_prompt = f"""Analyze this business data and provide comprehensive insights:

Dataset Summary: {data_summary}

Sample Data:
{json.dumps(sample_data, indent=2)}

Provide {analysis_type} analysis including:
1. Data quality assessment
2. Key trends and patterns
3. Statistical insights and metrics
4. Business recommendations
5. Anomaly detection
6. Performance indicators
7. Growth opportunities
8. Risk factors identification
9. Comparative analysis
10. Actionable next steps

Focus on business value and practical recommendations."""
            
            analysis = ai_services.chat_with_ai(analysis_prompt, "business_analysis")
            
            return {
                'success': True,
                'data_records': len(data),
                'analysis_type': analysis_type,
                'insights': analysis,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Business data analysis failed: {str(e)}"}
    
    def create_presentation_outline(self, topic: str, audience: str, duration: int = 30) -> Dict[str, Any]:
        """Create presentation outline and structure"""
        try:
            presentation_prompt = f"""Create a comprehensive presentation outline for:

Topic: {topic}
Audience: {audience}
Duration: {duration} minutes

Provide detailed outline including:
1. Title slide and introduction
2. Agenda and objectives
3. Main content sections with timing
4. Key points and supporting details
5. Visual suggestions for each section
6. Transition statements
7. Interactive elements or Q&A sections
8. Conclusion and call-to-action
9. Speaker notes and tips
10. Appendix materials

Format as a professional presentation structure with slide-by-slide breakdown."""
            
            outline = ai_services.chat_with_ai(presentation_prompt, "presentation_planning")
            
            # Save outline
            filename = f"presentation_outline_{topic.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.txt"
            filepath = os.path.join("downloads", filename)
            os.makedirs("downloads", exist_ok=True)
            
            with open(filepath, 'w') as f:
                f.write(outline)
            
            return {
                'success': True,
                'outline': outline,
                'filepath': filepath,
                'topic': topic,
                'audience': audience,
                'duration': duration
            }
            
        except Exception as e:
            return {"error": f"Presentation outline creation failed: {str(e)}"}

# Global instance
professional_tools_service = ProfessionalToolsService()