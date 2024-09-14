import requests
import json
from datetime import datetime

class GitHubIssueMiner:
    def __init__(self, token):
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def fetch_issues(self, repo, state='all', labels="bug"):
        issues = []
        page = 1
        while True:
            url = f"{self.base_url}/repos/{repo}/issues"
            params = {
                'state': state,
                'page': page,
                'per_page': 100,
                'labels': labels if labels else None
            }
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code != 200:
                raise Exception(f"API request failed: {response.status_code}, {response.text}")
            
            page_issues = response.json()
            if not page_issues:
                break
            
            for issue in page_issues:
                if 'pull_request' not in issue:  
                    issues.append(self.extract_issue_data(issue))
            
            page += 1
        
        return issues

    def extract_issue_data(self, issue):
        return {
            'issue_number': issue['number'],
            'issue_url': issue['html_url'],
            'title': issue['title'],
            'body': issue['body'],
            'labels': [label['name'] for label in issue['labels']],
            'num_comments': issue['comments'],
        }

    def mine_issues(self, repo, is_open=True, labels=None):
        state = 'open' if is_open else 'closed'
        return self.fetch_issues(repo, state, labels)

def save_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    token = "YOUR GITHUB TOKEN HERE"
    miner = GitHubIssueMiner(token)
    repo_list = ["microsoft/autogen", "joaomdmoura/crewAI", "langchain-ai/langchain", "xlang-ai/OpenAgents", "gpt-engineer-org/gpt-engineer", "Significant-Gravitas/AutoGPT", "OpenDevin/OpenDevin"]

    for repo_num in range(len(repo_list)):
        repo = repo_list[repo_num]
        is_open = False
        labels = None

        issues = miner.mine_issues(repo, is_open, labels)

        repo_name = repo.split('/')[-1]
        filename = f"github_issues_{repo_name}_{is_open}.json"
        save_to_json(issues, '../reports/Github/'+filename)

    print(f"Mined {len(issues)} issues and saved to {filename}")