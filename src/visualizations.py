"""
Visualization Module for Market Basket Analysis
Author: Vinisha Biju
"""

import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
import pandas as pd
import numpy as np

def plot_product_network(rules_df, top_n=20):
    """
    Create network graph showing product associations
    
    Parameters:
    -----------
    rules_df : DataFrame
        Association rules dataframe
    top_n : int
        Number of top rules to visualize
    """
    plt.figure(figsize=(15, 10))
    G = nx.DiGraph()
    
    # Add edges for top rules
    for idx, row in rules_df.head(top_n).iterrows():
        antecedent = list(row['antecedents'])[0]
        consequent = list(row['consequents'])[0]
        G.add_edge(antecedent, consequent, weight=row['lift'])
    
    # Calculate node positions
    pos = nx.spring_layout(G, k=2, iterations=50)
    
    # Draw network
    nx.draw_networkx_nodes(G, pos, node_size=3000, node_color='lightblue', alpha=0.7)
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')
    nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True, 
                          arrowsize=20, width=2, alpha=0.5)
    
    plt.title('Product Association Network (Top {} Rules)'.format(top_n), fontsize=16)
    plt.axis('off')
    plt.tight_layout()
    plt.savefig('outputs/product_network.png', dpi=300, bbox_inches='tight')
    print("Saved product network visualization")

def plot_lift_distribution(rules_df):
    """
    Plot distribution of lift values
    """
    plt.figure(figsize=(10, 6))
    plt.hist(rules_df['lift'], bins=50, color='steelblue', edgecolor='black', alpha=0.7)
    plt.axvline(rules_df['lift'].mean(), color='red', linestyle='--', 
                linewidth=2, label=f'Mean: {rules_df["lift"].mean():.2f}')
    plt.xlabel('Lift', fontsize=12)
    plt.ylabel('Frequency', fontsize=12)
    plt.title('Distribution of Lift Values in Association Rules', fontsize=14)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('outputs/lift_distribution.png', dpi=300)
    print("Saved lift distribution plot")

def plot_top_products_frequency(transactions, top_n=15):
    """
    Visualize most frequently purchased products
    
    Parameters:
    -----------
    transactions : list
        List of transaction lists
    top_n : int
        Number of top products to show
    """
    # Flatten transactions and count
    all_products = [item for transaction in transactions for item in transaction]
    product_counts = pd.Series(all_products).value_counts().head(top_n)
    
    plt.figure(figsize=(12, 6))
    product_counts.plot(kind='barh', color='coral')
    plt.xlabel('Frequency', fontsize=12)
    plt.ylabel('Product', fontsize=12)
    plt.title(f'Top {top_n} Most Frequently Purchased Products', fontsize=14)
    plt.tight_layout()
    plt.savefig('outputs/top_products_frequency.png', dpi=300)
    print("Saved top products frequency plot")

def create_summary_dashboard(rules_df, transactions):
    """
    Create comprehensive dashboard with multiple visualizations
    """
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # 1. Scatter: Support vs Confidence
    axes[0, 0].scatter(rules_df['support'], rules_df['confidence'], 
                      s=rules_df['lift']*30, alpha=0.5, c=rules_df['lift'], cmap='viridis')
    axes[0, 0].set_xlabel('Support')
    axes[0, 0].set_ylabel('Confidence')
    axes[0, 0].set_title('Support vs Confidence (sized by Lift)')
    axes[0, 0].grid(True, alpha=0.3)
    
    # 2. Lift Distribution
    axes[0, 1].hist(rules_df['lift'], bins=30, color='steelblue', edgecolor='black')
    axes[0, 1].axvline(rules_df['lift'].mean(), color='red', linestyle='--', linewidth=2)
    axes[0, 1].set_xlabel('Lift')
    axes[0, 1].set_ylabel('Frequency')
    axes[0, 1].set_title('Lift Value Distribution')
    axes[0, 1].grid(True, alpha=0.3)
    
    # 3. Top Rules by Lift
    top_rules = rules_df.nlargest(10, 'lift')
    rule_labels = [f"Rule {i+1}" for i in range(len(top_rules))]
    axes[1, 0].barh(rule_labels, top_rules['lift'], color='coral')
    axes[1, 0].set_xlabel('Lift')
    axes[1, 0].set_title('Top 10 Rules by Lift')
    axes[1, 0].invert_yaxis()
    
    # 4. Transaction Size Distribution
    transaction_sizes = [len(t) for t in transactions]
    axes[1, 1].hist(transaction_sizes, bins=20, color='green', edgecolor='black', alpha=0.7)
    axes[1, 1].set_xlabel('Items per Transaction')
    axes[1, 1].set_ylabel('Frequency')
    axes[1, 1].set_title('Transaction Size Distribution')
    axes[1, 1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('outputs/summary_dashboard.png', dpi=300)
    print("Saved summary dashboard")

def export_results_to_excel(rules_df, frequent_itemsets, output_path='outputs/analysis_results.xlsx'):
    """
    Export analysis results to Excel file
    """
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        # Clean rules dataframe
        rules_export = rules_df.copy()
        rules_export['antecedents'] = rules_export['antecedents'].apply(lambda x: ', '.join(list(x)))
        rules_export['consequents'] = rules_export['consequents'].apply(lambda x: ', '.join(list(x)))
        rules_export.to_excel(writer, sheet_name='Association Rules', index=False)
        
        # Export frequent itemsets
        itemsets_export = frequent_itemsets.copy()
        itemsets_export['itemsets'] = itemsets_export['itemsets'].apply(lambda x: ', '.join(list(x)))
        itemsets_export.to_excel(writer, sheet_name='Frequent Itemsets', index=False)
    
    print(f"Results exported to {output_path}")
