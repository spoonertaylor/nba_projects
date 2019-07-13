# Project: College Position Clustering
# Description: Cluster players into positional types based on their seasonal
# college box-score statistics
# Data Sources: Sports-Reference
# Last Updated: 7/12/2019


import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, silhouette_samples
from sklearn.neighbors import KNeighborsClassifier

import warnings
from sklearn.exceptions import DataConversionWarning
warnings.filterwarnings(action='ignore', category=DataConversionWarning)

# Plotting Style
plt.style.use('fivethirtyeight')

def elbow_plot(standardized_data, max_k):
    """
    Plots the Residual Sum of Squares for various numbers of clusters in the K-Means
    clustering algorithm. Displays a potential 'elbow' indicating an 'optimal'
    number of clusters.

    Args:
        standardized_data: pandas DataFrame with standardized data
        max_k: Maximum number of clusters with which to fit a K-Means algorithm

    Returns:
        None (Displays Plot)
    """
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
    """
    Plots the Silhouette Score for various numbers of clusters in the K-Means
    clustering algorithm. Displays a potential 'optimal' number of clusters.

    Args:
        standardized_data: pandas DataFrame with standardized data
        max_k: Maximum number of clusters with which to fit a K-Means algorithm

    Returns:
        None (Displays Plot)
    """
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
    """
    Plots the Silhouette Analysis for a specified number of clusters. Silhouette
    analysis can be used to study the separation distance between the resulting
    clusters. The silhouette plot displays a measure of how close each point in
    one cluster is to points in the neighboring clusters and thus provides a way
    to assess parameters like number of clusters visually. This measure has a
    range of [-1, 1].

    Silhouette coefficients (as these values are referred to as) near +1 indicate
    that the sample is far away from the neighboring clusters. A value of 0 indicates
    that the sample is on or very close to the decision boundary between two neighboring
    clusters and negative values indicate that those samples might have been assigned
    to the wrong cluster. (sklearn documentation)

    Args:
        X: pandas DataFrame with standardized data
        n_clusters: Number of clusters to build in the K-Means algorithm.

    Returns:
        None (Displays Plot)
    """
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
    # at the season level in additon to an aggregated 'Career' record.
    sports_ref = pd.read_csv('../../data/ncaa/sports_reference/player_data/combined/sports_ref_player_data.csv')

    # Read in Measurement Data (height and weight)
    measurables = pd.read_csv('../../data/nba/basketball_reference/player_data/measurements/player_measurements.csv')

    # Read in bridge table with sports-reference and basketball-reference id's to
    # join data together
    bridge = pd.read_csv('../../data/player_ids/player_table.csv')

    # Join dataframes
    sports_ref_merge = pd.merge(sports_ref, bridge, left_on='SPORTS_REF_ID', right_on='sportsref_id', how='inner')
    sports_ref_merge = sports_ref_merge[['PLAYER', 'SEASON', 'SCHOOL', 'CONFERENCE', 'G', 'GS', 'MP', 'PER',
       'TS%', 'eFG%', '3PAr', 'FTr', 'PProd', 'ORB%', 'DRB%', 'TRB%', 'AST%',
       'STL%', 'BLK%', 'TOV%', 'USG%', 'OWS', 'DWS', 'WS', 'WS/40', 'OBPM',
       'DBPM', 'BPM', 'PER40_FG', 'PER40_FGA', 'PER40_FG%', 'PER40_2P',
       'PER40_2PA', 'PER40_2P%', 'PER40_3P', 'PER40_3PA', 'PER40_3P%',
       'PER40_FT', 'PER40_FTA', 'PER40_FT%', 'PER40_TRB', 'PER40_AST',
       'PER40_STL', 'PER40_BLK', 'PER40_TOV', 'PER40_PF', 'PER40_PTS',
       'PER100_FG', 'PER100_FGA', 'PER100_FG%', 'PER100_2P', 'PER100_2PA',
       'PER100_2P%', 'PER100_3P', 'PER100_3PA', 'PER100_3P%', 'PER100_FT',
       'PER100_FTA', 'PER100_FT%', 'PER100_TRB', 'PER100_AST', 'PER100_STL',
       'PER100_BLK', 'PER100_TOV', 'PER100_PF', 'PER100_PTS', 'PER100_ORtg',
       'PER100_DRtg', 'SPORTS_REF_ID', 'bbref_id']]

    college_df = pd.merge(sports_ref_merge, measurables, on='bbref_id', how='left')

    # Features on which to cluster (same as NBA clustering)
    cluster_features = ['height', 'weight', '3PAr', 'ORB%', 'DRB%', 'AST%', 'BLK%', 'USG%', 'TS%']

    # Filter to records with complete information in the list of features above
    # on which we will cluster. Removes most players before 2010.
    complete_records = college_df[college_df[cluster_features].notnull().all(axis=1)]

    # Filter to records with incomplete information in the list of features above.
    # Includes mostly players from before 2010.
    incomplete_records = college_df[college_df[cluster_features].isnull().any(axis=1)]

    # Standardize features
    scaler = StandardScaler()
    X = scaler.fit_transform(complete_records[cluster_features])

    # Elbow Plot
    elbow_plot(X, 15)

    # Silhouette Score
    silhouette_score_plot(X, 15)

    # Silhouette Analysis
    cluster_and_plot(X, 3)

    # Cluster K=3 (Guards, Wings, Bigs)
    kmeans = KMeans(n_clusters=3, random_state=10)
    kmeans.fit(X)
    complete_records['POSITION_CLUSTER'] = kmeans.labels_
    complete_records['POSITION_CLUSTER'] = complete_records['POSITION_CLUSTER'].astype(str)

    # Scale Per-40 Features and fill missing Per-40 with global mean
    features_40 = ['PER40_FG', 'PER40_FGA', 'PER40_FG%', 'PER40_2P',
       'PER40_2PA', 'PER40_2P%', 'PER40_3P', 'PER40_3PA', 'PER40_3P%',
       'PER40_FT', 'PER40_FTA', 'PER40_FT%', 'PER40_TRB', 'PER40_AST',
       'PER40_STL', 'PER40_BLK', 'PER40_TOV', 'PER40_PF', 'PER40_PTS',
       'height', 'weight']
    X_train, y_train = scaler.fit_transform(complete_records[features_40].apply(lambda x: x.fillna(x.mean()),axis=0)), complete_records['POSITION_CLUSTER'].values
    X_test = scaler.fit_transform(incomplete_records[features_40].apply(lambda x: x.fillna(x.mean()),axis=0))

    # Classify records without complete information in the clustering step
    knn = KNeighborsClassifier(n_neighbors=5)
    knn.fit(X_train, y_train)
    incomplete_records['POSITION_CLUSTER'] = knn.predict(X_test)

    # Join dataframes
    df_out = pd.concat([complete_records, incomplete_records]) # [['PLAYER', 'SEASON', 'SPORTS_REF_ID', 'bbref_id', 'POSITION_CLUSTER']]
    df_out['POSITION_CLUSTER'] = df_out['POSITION_CLUSTER'].replace({'0': 'Wing', '1': 'Guard', '2': 'Big'})

    # Write Data
    df_out.to_csv('../../data/ncaa/sports_reference/player_data/positions/positions.csv', index=False)

    # Cluster EDA
    # Total Size of Cluster
    fig, ax = plt.subplots(figsize=(9, 5))
    sns.countplot(x='POSITION_CLUSTER', data=df_out[df_out['SEASON']=='Career'])
    ax.set_xlabel('Position Cluster', fontsize=12)
    ax.set_ylabel('Player Count', fontsize=12)
    plt.title('Player Count by Position Cluster', fontsize=18)
    plt.tight_layout()
    plt.show()

    # Plot Clustering Features
    fig, axs = plt.subplots(nrows=1, ncols=3, figsize=(18, 5), sharex=True)
    sns.violinplot(x='POSITION_CLUSTER', y='height', data=df_out[df_out['SEASON']=='Career'], cut=0, ax=axs[0])
    sns.violinplot(x='POSITION_CLUSTER', y='weight', data=df_out[df_out['SEASON']=='Career'], cut=0, ax=axs[1])
    sns.violinplot(x='POSITION_CLUSTER', y='3PAr', data=df_out[df_out['SEASON']=='Career'], cut=0, ax=axs[2])
    axs[0].set_xlabel('')
    axs[0].set_ylabel('Height (Inches)')
    axs[1].set_xlabel('')
    axs[1].set_ylabel('Weight (lbs.)')
    axs[2].set_xlabel('')
    axs[2].set_ylabel('3-Point Attempt Rate')
    axs[1].set_title('Distribution of Cluster Features by Position Cluster')
    plt.tight_layout()
    plt.show()

    fig, axs = plt.subplots(nrows=1, ncols=3, figsize=(18, 5), sharex=True)
    sns.violinplot(x='POSITION_CLUSTER', y='ORB%', data=df_out[df_out['SEASON']=='Career'], cut=0, ax=axs[0])
    sns.violinplot(x='POSITION_CLUSTER', y='DRB%', data=df_out[df_out['SEASON']=='Career'], cut=0, ax=axs[1])
    sns.violinplot(x='POSITION_CLUSTER', y='AST%', data=df_out[df_out['SEASON']=='Career'], cut=0, ax=axs[2])
    axs[0].set_xlabel('')
    axs[0].set_ylabel('Offensive Rebounding %')
    axs[1].set_xlabel('')
    axs[1].set_ylabel('Defensive Rebounding %')
    axs[2].set_xlabel('')
    axs[2].set_ylabel('Assist %')
    plt.tight_layout()
    plt.show()

    fig, axs = plt.subplots(nrows=1, ncols=3, figsize=(18, 5), sharex=True)
    sns.violinplot(x='POSITION_CLUSTER', y='BLK%', data=df_out[df_out['SEASON']=='Career'], cut=0, ax=axs[0])
    sns.violinplot(x='POSITION_CLUSTER', y='USG%', data=df_out[df_out['SEASON']=='Career'], cut=0, ax=axs[1])
    sns.violinplot(x='POSITION_CLUSTER', y='TS%', data=df_out[df_out['SEASON']=='Career'], cut=0, ax=axs[2])
    axs[0].set_xlabel('')
    axs[0].set_ylabel('Block %')
    axs[1].set_xlabel('Position Cluster')
    axs[1].set_ylabel('Usage %')
    axs[2].set_xlabel('')
    axs[2].set_ylabel('True Shooting %')
    plt.tight_layout()
    plt.show()
