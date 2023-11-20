import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm

def missing_data_check(df):
    total = df.isnull().sum()
    pct = (total / df.isnull().count()) * 100
    # output metrics table
    result = pd.concat([total, pct], axis = 1, keys = ['Total', 'Percent'])
    # add dtypes to output
    types = [str(df[col].dtype) for col in df.columns]
    result["Types"] = types
    return result

def plot_histograms(df, bins=10):
    num_features = len(df.columns)
    num_rows = (num_features + 1) // 2
    fig, ax = plt.subplots(nrows=num_rows, ncols=2, figsize=(10, 4 * num_rows))

    ax = ax.flatten()

    for i, feature in enumerate(df.columns):
        ax[i].hist(df[feature], bins=bins)
        ax[i].set_title(feature)
        ax[i].set_xlabel('Value')
        ax[i].set_ylabel('Frequency')
    
    plt.tight_layout()

    plt.show()