import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm

df = pd.read_csv('./rq4_raw.csv')
df = df[df['owner/repo'] != 'Total']
df['repo'] = df['owner/repo'].str.split('/').str[1]
num_repos = len(df['repo'].unique())
colors = cm.get_cmap('viridis', num_repos)
fig, axes = plt.subplots(2, 2, figsize=(20, 15))
fontsize = 25
labelsize = 20

for i, repo in enumerate(df['repo']):
    axes[0, 0].bar(repo, df['average_changes'][i], color=colors(i))
axes[0, 0].set_title('Average Changes per PR', fontsize=fontsize)
axes[0, 0].set_ylabel('Average Changes', fontsize=fontsize)
axes[0, 0].tick_params(axis='x', rotation=0, labelsize=labelsize)
axes[0, 0].tick_params(axis='y', rotation=0, labelsize=labelsize)

for i, repo in enumerate(df['repo']):
    axes[0, 1].bar(repo, df['average_changed_files'][i], color=colors(i))
axes[0, 1].set_title('Average Changed Files per PR', fontsize=fontsize)
axes[0, 1].set_ylabel('Average Changed Files', fontsize=fontsize)
axes[0, 1].tick_params(axis='x', rotation=0, labelsize=labelsize)
axes[0, 1].tick_params(axis='y', rotation=0, labelsize=labelsize)

for i, repo in enumerate(df['repo']):
    axes[1, 0].bar(repo, df['average_time'][i] / 86400, color=colors(i))
axes[1, 0].set_title('Average Resolution Time per PR', fontsize=fontsize)
axes[1, 0].set_ylabel('Average Time (days)', fontsize=fontsize)
axes[1, 0].tick_params(axis='x', rotation=0, labelsize=labelsize)
axes[1, 0].tick_params(axis='y', rotation=0, labelsize=labelsize)

for i, repo in enumerate(df['repo']):
    axes[1, 1].bar(repo, df['average_commits'][i], color=colors(i))
axes[1, 1].set_title('Average Commits per PR', fontsize=fontsize)
axes[1, 1].set_ylabel('Average Commits', fontsize=fontsize)
axes[1, 1].tick_params(axis='x', rotation=0, labelsize=labelsize)  
axes[1, 1].tick_params(axis='y', rotation=0, labelsize=labelsize)  


plt.tight_layout()
plt.savefig('rq4_visualizations.pdf', format='pdf')
plt.close()