import json
import os
import asyncio
import aiohttp
import hashlib
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
from ai_services import ai_services

class BlockchainWeb3Service:
    """Blockchain and Web3 integration with smart contracts, NFTs, and DeFi"""
    
    def __init__(self):
        self.blockchain_apis = {
            "ethereum": "https://api.etherscan.io/api",
            "bitcoin": "https://blockstream.info/api",
            "polygon": "https://api.polygonscan.com/api",
            "bsc": "https://api.bscscan.com/api",
            "coingecko": "https://api.coingecko.com/api/v3"
        }
        self.contract_templates = self.load_contract_templates()
        self.nft_standards = ["ERC-721", "ERC-1155", "ERC-998"]
    
    def load_contract_templates(self) -> Dict[str, str]:
        """Load smart contract templates"""
        return {
            "token": '''// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract {token_name} is ERC20, Ownable {{
    constructor() ERC20("{token_name}", "{token_symbol}") {{
        _mint(msg.sender, {initial_supply} * 10**decimals());
    }}
    
    function mint(address to, uint256 amount) public onlyOwner {{
        _mint(to, amount);
    }}
    
    function burn(uint256 amount) public {{
        _burn(msg.sender, amount);
    }}
}}''',
            
            "nft": '''// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

contract {nft_name} is ERC721, ERC721URIStorage, Ownable {{
    using Counters for Counters.Counter;
    Counters.Counter private _tokenIdCounter;
    
    constructor() ERC721("{nft_name}", "{nft_symbol}") {{}}
    
    function safeMint(address to, string memory uri) public onlyOwner {{
        uint256 tokenId = _tokenIdCounter.current();
        _tokenIdCounter.increment();
        _safeMint(to, tokenId);
        _setTokenURI(tokenId, uri);
    }}
    
    function tokenURI(uint256 tokenId) public view override(ERC721, ERC721URIStorage) returns (string memory) {{
        return super.tokenURI(tokenId);
    }}
    
    function _burn(uint256 tokenId) internal override(ERC721, ERC721URIStorage) {{
        super._burn(tokenId);
    }}
}}''',
            
            "defi": '''// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract {contract_name} is ReentrancyGuard, Ownable {{
    IERC20 public token;
    uint256 public rewardRate;
    uint256 public lastUpdateTime;
    uint256 public rewardPerTokenStored;
    
    mapping(address => uint256) public userRewardPerTokenPaid;
    mapping(address => uint256) public rewards;
    mapping(address => uint256) public balances;
    
    uint256 private _totalSupply;
    
    constructor(address _token, uint256 _rewardRate) {{
        token = IERC20(_token);
        rewardRate = _rewardRate;
    }}
    
    function stake(uint256 amount) external nonReentrant updateReward(msg.sender) {{
        require(amount > 0, "Cannot stake 0");
        _totalSupply += amount;
        balances[msg.sender] += amount;
        token.transferFrom(msg.sender, address(this), amount);
        emit Staked(msg.sender, amount);
    }}
    
    function withdraw(uint256 amount) external nonReentrant updateReward(msg.sender) {{
        require(amount > 0, "Cannot withdraw 0");
        _totalSupply -= amount;
        balances[msg.sender] -= amount;
        token.transfer(msg.sender, amount);
        emit Withdrawn(msg.sender, amount);
    }}
    
    modifier updateReward(address account) {{
        rewardPerTokenStored = rewardPerToken();
        lastUpdateTime = block.timestamp;
        if (account != address(0)) {{
            rewards[account] = earned(account);
            userRewardPerTokenPaid[account] = rewardPerTokenStored;
        }}
        _;
    }}
    
    function rewardPerToken() public view returns (uint256) {{
        if (_totalSupply == 0) {{
            return rewardPerTokenStored;
        }}
        return rewardPerTokenStored + (((block.timestamp - lastUpdateTime) * rewardRate * 1e18) / _totalSupply);
    }}
    
    function earned(address account) public view returns (uint256) {{
        return ((balances[account] * (rewardPerToken() - userRewardPerTokenPaid[account])) / 1e18) + rewards[account];
    }}
    
    event Staked(address indexed user, uint256 amount);
    event Withdrawn(address indexed user, uint256 amount);
}}'''
        }
    
    async def generate_smart_contract(self, contract_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate smart contract code"""
        try:
            if contract_type not in self.contract_templates:
                contract_type = "token"
            
            template = self.contract_templates[contract_type]
            
            # Fill template with parameters
            contract_code = template.format(**parameters)
            
            # Generate additional contract details
            contract_details = await self._analyze_contract(contract_code, contract_type)
            
            # Generate deployment instructions
            deployment_instructions = self._generate_deployment_instructions(contract_type, parameters)
            
            return {
                'success': True,
                'contract_type': contract_type,
                'contract_code': contract_code,
                'parameters': parameters,
                'analysis': contract_details,
                'deployment_instructions': deployment_instructions,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Smart contract generation failed: {str(e)}"}
    
    async def _analyze_contract(self, contract_code: str, contract_type: str) -> Dict[str, Any]:
        """Analyze smart contract for security and optimization"""
        analysis_prompt = f"""Analyze this {contract_type} smart contract for:

{contract_code}

Provide comprehensive analysis including:
1. Security vulnerabilities and risks
2. Gas optimization opportunities
3. Best practices compliance
4. Potential attack vectors
5. Access control mechanisms
6. Upgradeability considerations
7. Testing recommendations
8. Deployment checklist
9. Integration considerations
10. Maintenance requirements

Focus on production readiness and security."""
        
        analysis = ai_services.chat_with_ai(analysis_prompt, "contract_analysis")
        
        return {
            'security_score': self._calculate_security_score(contract_code),
            'gas_efficiency': self._estimate_gas_efficiency(contract_code),
            'analysis': analysis,
            'recommendations': self._extract_recommendations(analysis)
        }
    
    def _calculate_security_score(self, contract_code: str) -> int:
        """Calculate basic security score"""
        score = 100
        
        # Check for common security patterns
        if "require(" not in contract_code:
            score -= 20
        if "onlyOwner" not in contract_code and "Ownable" in contract_code:
            score -= 15
        if "ReentrancyGuard" not in contract_code:
            score -= 10
        if "_burn(" in contract_code and "onlyOwner" not in contract_code:
            score -= 25
        
        return max(score, 0)
    
    def _estimate_gas_efficiency(self, contract_code: str) -> str:
        """Estimate gas efficiency"""
        if "view" in contract_code and "pure" in contract_code:
            return "High"
        elif "mapping" in contract_code:
            return "Medium"
        else:
            return "Low"
    
    def _extract_recommendations(self, analysis: str) -> List[str]:
        """Extract key recommendations from analysis"""
        recommendations = []
        lines = analysis.split('\n')
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['recommend', 'should', 'consider', 'improve']):
                recommendations.append(line.strip())
        
        return recommendations[:5]  # Top 5 recommendations
    
    def _generate_deployment_instructions(self, contract_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate deployment instructions"""
        return {
            'prerequisites': [
                'Node.js and npm installed',
                'Hardhat or Truffle framework',
                'MetaMask wallet configured',
                'Test ETH for deployment'
            ],
            'steps': [
                '1. Install dependencies: npm install @openzeppelin/contracts',
                '2. Compile contract: npx hardhat compile',
                '3. Deploy to testnet: npx hardhat run scripts/deploy.js --network sepolia',
                '4. Verify contract: npx hardhat verify --network sepolia DEPLOYED_CONTRACT_ADDRESS',
                '5. Test contract functions'
            ],
            'networks': {
                'mainnet': 'Ethereum Mainnet (use for production)',
                'sepolia': 'Sepolia Testnet (recommended for testing)',
                'polygon': 'Polygon Mainnet (lower gas fees)',
                'bsc': 'Binance Smart Chain'
            }
        }
    
    async def create_nft_collection(self, collection_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate NFT collection with metadata"""
        try:
            collection_name = collection_data.get('name', 'MyNFTCollection')
            collection_size = collection_data.get('size', 10)
            theme = collection_data.get('theme', 'abstract art')
            
            # Generate contract
            contract_params = {
                'nft_name': collection_name,
                'nft_symbol': collection_data.get('symbol', 'MNFT')
            }
            
            contract_result = await self.generate_smart_contract('nft', contract_params)
            
            # Generate metadata for each NFT
            nft_metadata = []
            for i in range(collection_size):
                metadata = await self._generate_nft_metadata(i + 1, theme, collection_name)
                nft_metadata.append(metadata)
            
            # Generate collection metadata
            collection_metadata = self._generate_collection_metadata(collection_data, nft_metadata)
            
            return {
                'success': True,
                'collection_name': collection_name,
                'size': collection_size,
                'contract': contract_result,
                'nft_metadata': nft_metadata,
                'collection_metadata': collection_metadata,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"NFT collection creation failed: {str(e)}"}
    
    async def _generate_nft_metadata(self, token_id: int, theme: str, collection_name: str) -> Dict[str, Any]:
        """Generate metadata for individual NFT"""
        metadata_prompt = f"""Create unique NFT metadata for token #{token_id} in the {collection_name} collection with {theme} theme.

Generate creative attributes including:
1. Unique name and description
2. Rarity traits and attributes
3. Visual characteristics
4. Special properties
5. Background story

Format as standard NFT metadata JSON."""
        
        metadata_content = ai_services.chat_with_ai(metadata_prompt, "nft_metadata")
        
        # Generate attributes
        attributes = self._generate_nft_attributes(theme, token_id)
        
        return {
            'name': f"{collection_name} #{token_id}",
            'description': f"Unique {theme} NFT from {collection_name} collection",
            'image': f"https://example.com/nft/{collection_name.lower()}/{token_id}.png",
            'attributes': attributes,
            'token_id': token_id,
            'generated_content': metadata_content
        }
    
    def _generate_nft_attributes(self, theme: str, token_id: int) -> List[Dict[str, Any]]:
        """Generate NFT attributes based on theme"""
        base_attributes = [
            {'trait_type': 'Theme', 'value': theme.title()},
            {'trait_type': 'Token ID', 'value': token_id},
            {'trait_type': 'Generation', 'value': 1}
        ]
        
        # Theme-specific attributes
        theme_attributes = {
            'abstract art': [
                {'trait_type': 'Color Palette', 'value': 'Vibrant'},
                {'trait_type': 'Complexity', 'value': 'High'},
                {'trait_type': 'Style', 'value': 'Modern'}
            ],
            'fantasy': [
                {'trait_type': 'Element', 'value': 'Fire'},
                {'trait_type': 'Rarity', 'value': 'Legendary'},
                {'trait_type': 'Power Level', 'value': '9000'}
            ],
            'cyberpunk': [
                {'trait_type': 'Tech Level', 'value': 'Advanced'},
                {'trait_type': 'Neon Color', 'value': 'Blue'},
                {'trait_type': 'Augmentation', 'value': 'Neural'}
            ]
        }
        
        specific_attributes = theme_attributes.get(theme.lower(), theme_attributes['abstract art'])
        return base_attributes + specific_attributes
    
    def _generate_collection_metadata(self, collection_data: Dict[str, Any], nft_metadata: List[Dict]) -> Dict[str, Any]:
        """Generate collection-level metadata"""
        return {
            'name': collection_data.get('name', 'MyNFTCollection'),
            'description': collection_data.get('description', 'A unique NFT collection'),
            'image': collection_data.get('banner_image', 'https://example.com/collection-banner.png'),
            'external_url': collection_data.get('website', 'https://example.com'),
            'seller_fee_basis_points': collection_data.get('royalty', 250),  # 2.5%
            'fee_recipient': collection_data.get('creator_address', '0x...'),
            'total_supply': len(nft_metadata),
            'traits_distribution': self._calculate_traits_distribution(nft_metadata)
        }
    
    def _calculate_traits_distribution(self, nft_metadata: List[Dict]) -> Dict[str, Dict[str, int]]:
        """Calculate rarity distribution of traits"""
        distribution = {}
        
        for nft in nft_metadata:
            for attribute in nft.get('attributes', []):
                trait_type = attribute['trait_type']
                trait_value = str(attribute['value'])
                
                if trait_type not in distribution:
                    distribution[trait_type] = {}
                
                if trait_value not in distribution[trait_type]:
                    distribution[trait_type][trait_value] = 0
                
                distribution[trait_type][trait_value] += 1
        
        return distribution
    
    async def create_dao_structure(self, dao_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create Decentralized Autonomous Organization structure"""
        try:
            dao_prompt = f"""Design a comprehensive DAO structure for: {dao_data.get('name', 'MyDAO')}

Purpose: {dao_data.get('purpose', 'Community governance')}
Token Supply: {dao_data.get('token_supply', 1000000)}
Governance Model: {dao_data.get('governance_model', 'token-based')}

Create complete DAO framework including:
1. Governance token contract
2. Voting mechanisms and proposals
3. Treasury management
4. Member roles and permissions
5. Decision-making processes
6. Smart contract interactions
7. Community guidelines
8. Token distribution strategy
9. Proposal submission process
10. Execution mechanisms

Provide technical implementation and governance structure."""
            
            dao_structure = ai_services.chat_with_ai(dao_prompt, "dao_creation")
            
            # Generate governance token contract
            token_params = {
                'token_name': f"{dao_data.get('name', 'MyDAO')}Token",
                'token_symbol': dao_data.get('token_symbol', 'DAO'),
                'initial_supply': dao_data.get('token_supply', 1000000)
            }
            
            governance_contract = await self.generate_smart_contract('token', token_params)
            
            return {
                'success': True,
                'dao_name': dao_data.get('name', 'MyDAO'),
                'structure': dao_structure,
                'governance_contract': governance_contract,
                'token_params': token_params,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"DAO creation failed: {str(e)}"}
    
    async def get_defi_analytics(self, protocol: str = "all") -> Dict[str, Any]:
        """Get DeFi protocol analytics from public APIs"""
        try:
            # Using DeFiPulse and CoinGecko free endpoints
            defi_url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&category=decentralized_finance_defi&order=market_cap_desc&per_page=20&page=1"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(defi_url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        analytics = {
                            'total_protocols': len(data),
                            'top_protocols': [],
                            'market_summary': {
                                'total_market_cap': 0,
                                'total_volume_24h': 0,
                                'average_price_change_24h': 0
                            }
                        }
                        
                        for coin in data[:10]:
                            protocol_data = {
                                'name': coin.get('name', ''),
                                'symbol': coin.get('symbol', '').upper(),
                                'price': coin.get('current_price', 0),
                                'market_cap': coin.get('market_cap', 0),
                                'volume_24h': coin.get('total_volume', 0),
                                'price_change_24h': coin.get('price_change_percentage_24h', 0),
                                'rank': coin.get('market_cap_rank', 0)
                            }
                            analytics['top_protocols'].append(protocol_data)
                            
                            # Add to totals
                            analytics['market_summary']['total_market_cap'] += protocol_data['market_cap']
                            analytics['market_summary']['total_volume_24h'] += protocol_data['volume_24h']
                            analytics['market_summary']['average_price_change_24h'] += protocol_data['price_change_24h']
                        
                        # Calculate averages
                        if analytics['top_protocols']:
                            analytics['market_summary']['average_price_change_24h'] /= len(analytics['top_protocols'])
                        
                        return {
                            'success': True,
                            'analytics': analytics,
                            'timestamp': datetime.now().isoformat()
                        }
            
            return {"error": "DeFi analytics not available"}
            
        except Exception as e:
            return {"error": f"DeFi analytics failed: {str(e)}"}
    
    async def create_trading_bot_strategy(self, strategy_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create cryptocurrency trading bot strategy"""
        try:
            strategy_prompt = f"""Create a comprehensive cryptocurrency trading bot strategy:

Strategy Type: {strategy_data.get('strategy_type', 'DCA')}
Risk Level: {strategy_data.get('risk_level', 'medium')}
Target Assets: {strategy_data.get('assets', ['BTC', 'ETH'])}
Budget: ${strategy_data.get('budget', 1000)}

Develop complete trading strategy including:
1. Entry and exit conditions
2. Risk management rules
3. Position sizing algorithms
4. Stop-loss and take-profit levels
5. Market analysis indicators
6. Backtesting methodology
7. Performance metrics
8. Error handling and failsafes
9. API integration requirements
10. Monitoring and alerting system

Provide detailed implementation plan and code structure."""
            
            strategy = ai_services.chat_with_ai(strategy_prompt, "trading_strategy")
            
            # Generate strategy configuration
            strategy_config = self._create_strategy_config(strategy_data)
            
            return {
                'success': True,
                'strategy_type': strategy_data.get('strategy_type', 'DCA'),
                'strategy_details': strategy,
                'configuration': strategy_config,
                'risk_assessment': self._assess_strategy_risk(strategy_data),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Trading strategy creation failed: {str(e)}"}
    
    def _create_strategy_config(self, strategy_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create trading strategy configuration"""
        return {
            'strategy_name': strategy_data.get('name', 'My Trading Strategy'),
            'assets': strategy_data.get('assets', ['BTC', 'ETH']),
            'budget': strategy_data.get('budget', 1000),
            'risk_level': strategy_data.get('risk_level', 'medium'),
            'max_drawdown': {'low': 5, 'medium': 10, 'high': 20}.get(strategy_data.get('risk_level', 'medium'), 10),
            'rebalance_frequency': strategy_data.get('rebalance_frequency', 'daily'),
            'indicators': ['RSI', 'MACD', 'Moving Average'],
            'exchanges': ['Binance', 'Coinbase Pro', 'Kraken'],
            'active': False,
            'created_at': datetime.now().isoformat()
        }
    
    def _assess_strategy_risk(self, strategy_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess trading strategy risk"""
        risk_level = strategy_data.get('risk_level', 'medium')
        budget = strategy_data.get('budget', 1000)
        
        risk_scores = {
            'low': {'score': 3, 'description': 'Conservative approach with capital preservation'},
            'medium': {'score': 6, 'description': 'Balanced risk-reward strategy'},
            'high': {'score': 9, 'description': 'Aggressive strategy with higher volatility'}
        }
        
        return {
            'risk_score': risk_scores.get(risk_level, risk_scores['medium'])['score'],
            'risk_description': risk_scores.get(risk_level, risk_scores['medium'])['description'],
            'recommended_budget': min(budget * 0.1, 100),  # Risk only 10% or $100 max for testing
            'warnings': self._generate_risk_warnings(risk_level, budget)
        }
    
    def _generate_risk_warnings(self, risk_level: str, budget: int) -> List[str]:
        """Generate risk warnings for trading strategy"""
        warnings = [
            "Cryptocurrency trading involves significant risk of loss",
            "Past performance does not guarantee future results",
            "Only invest what you can afford to lose"
        ]
        
        if risk_level == 'high':
            warnings.append("High-risk strategies can result in substantial losses")
        
        if budget > 10000:
            warnings.append("Consider starting with a smaller amount for testing")
        
        return warnings

# Global instance
blockchain_web3_service = BlockchainWeb3Service()