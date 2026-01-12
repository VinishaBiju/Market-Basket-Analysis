"""
Market Basket Analysis - Apriori Algorithm Implementation
Author: Vinisha Biju
Project: Retail Business Intelligence & Product Association Analysis
"""

import pandas as pd
import numpy as np
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

class MarketBasketAnalyzer:
    """
    Market Basket Analysis using Apriori Algorithm
    Identifies product associations and generates cross-selling recommendations
    """
    
    def __init__(self, min_support=0.05, min_confidence=0.4, min_lift=1.5):
        """
        Initialize Market Basket Analyzer
        
        Parameters:
        -----------
        min_support : float
            Minimum support threshold (default: 0.05 or 5%)
        min_confidence : float
            Minimum confidence threshold (default: 0.4 or 40%)
        min_lift : float
            Minimum lift threshold (default: 1.5)
        """
        self.min_support = min_support
        self.min_confidence = min_confidence
        self.min_lift = min_lift
        self.transactions = None
        self.basket_encoded = None
        self.frequent_itemsets = None
        self.rules = None
        
    def load_transactions(self, file_path, transaction_col='TransactionID', item_col='Product'):
        """
        Load transaction data from CSV file
        
        Parameters:
        -----------
        file_path : str
            Path to CSV file containing transaction data
        transaction_col : str
            Column name for transaction IDs
        item_col : str
            Column name for product/item names
        """
        df = pd.read_csv(file_path)
        self.transactions = df.groupby(transaction_col)[item_col].apply(list).values.tolist()
        print(f"Loaded {len(self.transactions)} transactions")
        return self
    
    def encode_transactions(self):
        """
        Encode transactions into one-hot encoded format for Apriori algorithm
        """
        te = TransactionEncoder()
        te_ary = te.fit(self.transactions).transform(self.transactions)
        self.basket_encoded = pd.DataFrame(te_ary, columns=te.columns_)
        print(f"Encoded {len(self.basket_encoded.columns)} unique products")
        return self
    
    def find_frequent_itemsets(self):
        """
        Apply Apriori algorithm to find frequent itemsets
        """
        self.frequent_itemsets = apriori(self.basket_encoded, 
                                        min_support=self.min_support, 
                                        use_colnames=True)
        print(f"Found {len(self.frequent_itemsets)} frequent itemsets")
        return self
    
    def generate_association_rules(self, metric='lift'):
        """
        Generate association rules from frequent itemsets
        
        Parameters:
        -----------
        metric : str
            Metric to evaluate rules ('lift', 'confidence', 'support')
        """
        self.rules = association_rules(self.frequent_itemsets, 
                                      metric=metric, 
                                      min_threshold=self.min_lift)
        
        # Filter by confidence threshold
        self.rules = self.rules[self.rules['confidence'] >= self.min_confidence]
        
        # Sort by lift (strongest associations first)
        self.rules = self.rules.sort_values('lift', ascending=False)
        
        print(f"Generated {len(self.rules)} association rules")
        return self
    
    def get_top_associations(self, n=10):
        """
        Get top N product associations by lift
        
        Parameters:
        -----------
        n : int
            Number of top associations to return
        """
        top_rules = self.rules.head(n)[['antecedents', 'consequents', 'support', 
                                       'confidence', 'lift']].copy()
        
        # Convert frozensets to readable strings
        top_rules['antecedents'] = top_rules['antecedents'].apply(lambda x: ', '.join(list(x)))
        top_rules['consequents'] = top_rules['consequents'].apply(lambda x: ', '.join(list(x)))
        
        return top_rules
    
    def plot_support_confidence(self, top_n=20):
        """
        Visualize support vs confidence for top association rules
        """
        plt.figure(figsize=(12, 6))
        top_rules = self.rules.head(top_n)
        
        scatter = plt.scatter(top_rules['support'], 
                            top_rules['confidence'],
                            s=top_rules['lift']*50,
                            c=top_rules['lift'],
                            cmap='viridis',
                            alpha=0.6)
        
        plt.xlabel('Support', fontsize=12)
        plt.ylabel('Confidence', fontsize=12)
        plt.title('Association Rules: Support vs Confidence (sized by Lift)', fontsize=14)
        plt.colorbar(scatter, label='Lift')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig('outputs/support_confidence_plot.png', dpi=300)
        print("Saved support-confidence plot")
        return self
    
    def plot_top_rules_heatmap(self, top_n=15):
        """
        Create heatmap of top association rules
        """
        plt.figure(figsize=(10, 8))
        top_rules = self.rules.head(top_n)
        
        # Create matrix for heatmap
        heatmap_data = top_rules[['support', 'confidence', 'lift']].values
        
        sns.heatmap(heatmap_data.T, 
                   annot=True, 
                   fmt='.2f',
                   cmap='YlOrRd',
                   xticklabels=[f"Rule {i+1}" for i in range(len(top_rules))],
                   yticklabels=['Support', 'Confidence', 'Lift'])
        
        plt.title(f'Top {top_n} Association Rules Metrics', fontsize=14)
        plt.tight_layout()
        plt.savefig('outputs/association_rules_heatmap.png', dpi=300)
        print("Saved association rules heatmap")
        return self
    
    def get_product_recommendations(self, product_name):
        """
        Get cross-sell recommendations for a specific product
        
        Parameters:
        -----------
        product_name : str
            Product name to get recommendations for
        """
        recommendations = []
        
        for _, rule in self.rules.iterrows():
            antecedents = list(rule['antecedents'])
            consequents = list(rule['consequents'])
            
            if product_name in antecedents:
                recommendations.append({
                    'recommended_product': ', '.join(consequents),
                    'confidence': rule['confidence'],
                    'lift': rule['lift']
                })
        
        return pd.DataFrame(recommendations).sort_values('lift', ascending=False)
    
    def generate_summary_report(self):
        """
        Generate comprehensive analysis summary
        """
        report = {
            'total_transactions': len(self.transactions),
            'unique_products': len(self.basket_encoded.columns),
            'frequent_itemsets_found': len(self.frequent_itemsets),
            'association_rules_generated': len(self.rules),
            'avg_support': self.rules['support'].mean(),
            'avg_confidence': self.rules['confidence'].mean(),
            'avg_lift': self.rules['lift'].mean(),
            'top_product_pair': {
                'products': f"{list(self.rules.iloc[0]['antecedents'])[0]} -> {list(self.rules.iloc[0]['consequents'])[0]}",
                'lift': self.rules.iloc[0]['lift'],
                'confidence': self.rules.iloc[0]['confidence']
            }
        }
        
        return report


def main():
    """
    Main execution function for Market Basket Analysis
    """
    print("=" * 60)
    print("Market Basket Analysis - Retail Product Associations")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = MarketBasketAnalyzer(min_support=0.05, 
                                   min_confidence=0.4, 
                                   min_lift=1.5)
    
    # Load and process data
    print("\nStep 1: Loading transaction data...")
    # analyzer.load_transactions('data/transactions.csv')
    
    print("\nStep 2: Encoding transactions...")
    # analyzer.encode_transactions()
    
    print("\nStep 3: Finding frequent itemsets...")
    # analyzer.find_frequent_itemsets()
    
    print("\nStep 4: Generating association rules...")
    # analyzer.generate_association_rules()
    
    print("\nStep 5: Creating visualizations...")
    # analyzer.plot_support_confidence()
    # analyzer.plot_top_rules_heatmap()
    
    print("\n" + "=" * 60)
    print("Analysis complete! Check outputs/ folder for results.")
    print("=" * 60)

if __name__ == "__main__":
    main()
