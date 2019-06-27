# Project: College Position Clustering
# Description: Cluster players into positional types based on their seasonal
# college box-score statistics
# Data Sources: Sports-Reference
# Last Updated: 6/26/2019


import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics import silhouette_score, silhouette_samples

# Plotting Style
plt.style.use('fivethirtyeight')

def elbow_plot(standardized_data, max_k):
    ks = list(range(2, max_k))
    rss_list = []
    for k in ks:
        model = KMeans(n_clusters=k, random_state=10, n_jobs=-1)
        model.fit(standardized_data)
        rss_list.append(-model.score(standardized_data))
    fig, ax = plt.subplots(figsize=(18, 5))
    sns.lineplot(ks, rss_list)
    ax.set_xlabel('Number of Clusters')
    ax.set_ylabel('RSS')
    ax.set_xticks(ks)
    plt.title('College Advance/Per100\nElbow Plot')
    plt.tight_layout()
    plt.show()

def silhouette_score_plot(standardized_data, max_k):
    def get_silhouette_score(nclust):
        km = KMeans(nclust, random_state=10, n_jobs=-1)
        km.fit(standardized_data)
        sil_avg = silhouette_score(standardized_data, km.labels_)
        return sil_avg

    fig, ax = plt.subplots(figsize=(18, 5))
    sil_scores = [get_silhouette_score(i) for i in range(2,max_k)]
    sns.lineplot(range(2, max_k), sil_scores)
    ax.set_xlabel('Number of Clusters')
    ax.set_ylabel('Silhouette Score')
    ax.set_xticks(range(2, max_k))
    plt.title('College Advance/Per100\nSilhouette Score vs K')
    plt.tight_layout()
    plt.show()

def cluster_and_plot(X, n_clusters):
    # Create a subplot with 1 row and 2 columns
    fig, (ax1, ax2) = plt.subplots(nrows=1, ncols=2, figsize=(18, 5))

    # The 1st subplot is the silhouette plot
    # The silhouette coefficient can range from -1, 1 but in this example all
    # lie within [-0.1, 1]
    ax1.set_xlim([-0.1, 1])
    # The (n_clusters+1)*10 is for inserting blank space between silhouette
    # plots of individual clusters, to demarcate them clearly.
    ax1.set_ylim([0, len(X) + (n_clusters + 1) * 10])

    # Initialize the clusterer with n_clusters value and a random generator
    # seed of 10 for reproducibility.
    clusterer = KMeans(n_clusters=n_clusters, random_state=10)
    cluster_labels = clusterer.fit_predict(X)

    # The silhouette_score gives the average value for all the samples.
    # This gives a perspective into the density and separation of the formed
    # clusters
    silhouette_avg = silhouette_score(X, cluster_labels)
    print("For n_clusters =", n_clusters,
          "The average silhouette_score is :", silhouette_avg)

    # Compute the silhouette scores for each sample
    sample_silhouette_values = silhouette_samples(X, cluster_labels)

    y_lower = 10
    for i in range(n_clusters):
        # Aggregate the silhouette scores for samples belonging to
        # cluster i, and sort them
        ith_cluster_silhouette_values = \
            sample_silhouette_values[cluster_labels == i]

        ith_cluster_silhouette_values.sort()

        size_cluster_i = ith_cluster_silhouette_values.shape[0]
        y_upper = y_lower + size_cluster_i

        cmap = cm.get_cmap("Spectral")
        color = cmap(float(i) / n_clusters)
        ax1.fill_betweenx(np.arange(y_lower, y_upper),
                          0, ith_cluster_silhouette_values,
                          facecolor=color, edgecolor=color, alpha=0.7)

        # Label the silhouette plots with their cluster numbers at the middle
        ax1.text(-0.05, y_lower + 0.5 * size_cluster_i, str(i))

        # Compute the new y_lower for next plot
        y_lower = y_upper + 10  # 10 for the 0 samples

    ax1.set_title("The silhouette plot for the various clusters.")
    ax1.set_xlabel("The silhouette coefficient values")
    ax1.set_ylabel("Cluster label")

    # The vertical line for average silhoutte score of all the values
    ax1.axvline(x=silhouette_avg, color="red", linestyle="--")

    ax1.set_yticks([])  # Clear the yaxis labels / ticks
    ax1.set_xticks([-0.1, 0, 0.2, 0.4, 0.6, 0.8, 1])

    # 2nd Plot showing the actual clusters formed
    cmap = cm.get_cmap("Spectral")
    colors = cmap(cluster_labels.astype(float) / n_clusters)
    ax2.scatter(X[:, 0], X[:, 1], marker='.', s=30, lw=0, alpha=0.7,
                c=colors)

    # Labeling the clusters
    centers = clusterer.cluster_centers_
    # Draw white circles at cluster centers
    ax2.scatter(centers[:, 0], centers[:, 1],
                marker='o', c="white", alpha=1, s=200)

    for i, c in enumerate(centers):
        ax2.scatter(c[0], c[1], marker='$%d$' % i, alpha=1, s=50)

    ax2.set_title("The visualization of the clustered data.")
    ax2.set_xlabel("Feature space for the 1st feature")
    ax2.set_ylabel("Feature space for the 2nd feature")

    plt.suptitle(("Silhouette analysis for KMeans clustering on sample data "
                  "with n_clusters = %d" % n_clusters),
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.subplots_adjust(top=0.85)
    plt.show()



if __name__=='__main__':
    # Read in college statistics (per 100 possession, per 40 minutes, and advanced)
    # for all players who played in the NBA between 2004 and 2019. Records are
    # at the season level in addiiton to an aggregated 'Career' record.
    sports_ref = pd.read_csv('../../data/ncaa/sports_reference/player_data/combined/sports_ref_player_data.csv')

    # Features on which to cluster
    cluster_features = ['G', 'GS', 'MP', 'PER',
       'TS%', 'eFG%', '3PAr', 'FTr', 'PProd', 'ORB%', 'DRB%', 'TRB%', 'AST%',
       'STL%', 'BLK%', 'TOV%', 'USG%', 'OWS', 'DWS', 'WS', 'WS/40', 'OBPM',
       'DBPM', 'BPM', 'PER100_FG', 'PER100_FGA', 'PER100_FG%', 'PER100_2P', 'PER100_2PA',
       'PER100_2P%', 'PER100_3P', 'PER100_3PA', 'PER100_3P%', 'PER100_FT',
       'PER100_FTA', 'PER100_FT%', 'PER100_TRB', 'PER100_AST', 'PER100_STL',
       'PER100_BLK', 'PER100_TOV', 'PER100_PF', 'PER100_PTS', 'PER100_ORtg',
       'PER100_DRtg']

    # Filter to records with Per 100 Possession and Advanced  data
    # (removes most players before 2010). This is the group on which to cluster.
    per100 = sports_ref[sports_ref[cluster_features].notnull().all(axis=1)]

    # Filter to records without Per 100 Possessions and Advance data
    # (records before 2010)
    non_per100 = sports_ref[sports_ref[cluster_features].isnull().any(axis=1)]

    # Standardize features
    scaler = StandardScaler()
    X = scaler.fit_transform(per100[cluster_features])

    # Elbow Plot
    elbow_plot(X, 15)

    # Silhouette Score
    silhouette_score_plot(X, 15)

    # Silhouette Analysis
    cluster_and_plot(X, 4)
