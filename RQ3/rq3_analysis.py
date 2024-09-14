import json
from collections import Counter, OrderedDict
from typing import Dict, List
import matplotlib.pyplot as plt
import numpy as np

# Define label mappings 
BUG_TYPE_LABELS = OrderedDict([
    ("A1", "tool integration issue"),
    ("A2", "model integration issue"),
    ("A3", "api compatibility and dependency issue"),
    ("A4", "framework setup issue"),
    ("A5", "data format problem"),
    ("A6", "memory management issue"),
    ("A7", "context window overflow"),
    ("A8", "hallucination"),
    ("A9", "other")
])

DEVELOPMENT_CYCLE_LABELS = OrderedDict([
    ("D1", "Preprocessing Stage"),
    ("D2", "Agent Development and Integration Stage"),
    ("D3", "Postprocessing Stage"),
    ("D4", "Unknown")
])

def get_label(category: str, value: str) -> str:
    if category == 'bug_type':
        return next((k for k, v in BUG_TYPE_LABELS.items() if v.lower() == value.lower()), "Unknown")
    elif category == 'development_cycle':
        return next((k for k, v in DEVELOPMENT_CYCLE_LABELS.items() if v.lower() == value.lower()), "Unknown")
    return value

def analyze_json(file_paths: List[str]) -> Dict[str, Counter]:
    categories = ['bug_type', 'development_cycle']
    stats = {category: Counter() for category in categories}
    combinations = Counter()

    for file_path in file_paths:
        with open(file_path, 'r') as f:
            data = json.load(f)
            for issue in data.values():
                for category in categories:
                    label = get_label(category, issue[category])
                    stats[category][label] += 1

                bug_type_label = get_label('bug_type', issue['bug_type'])
                development_cycle_label = get_label('development_cycle', issue['development_cycle'])

                combinations[f"{bug_type_label} + {development_cycle_label}"] += 1

    stats['combinations'] = combinations
    return stats

def calculate_percentages(counter: Counter) -> Dict[str, float]:
    total = sum(counter.values())
    return {item: (count / total) * 100 for item, count in counter.items()}

def print_and_save_rq3_analysis(stats: Dict[str, Counter]):
    output = []

    # 1. Calculate and print the percentage of bugs in each development cycle stage
    development_cycle_percentages = calculate_percentages(stats['development_cycle'])
    output.append("1. Percentage of bugs in each development cycle stage:")
    for stage, percentage in development_cycle_percentages.items():
        label = DEVELOPMENT_CYCLE_LABELS.get(stage, "Unknown")
        if label == "Unknown":
            print(f"Unknown development cycle stage: {stage}")
        output.append(f"   {label} ({stage}): {percentage:.2f}%")

    # 2. Calculate and print the top 5 most frequent combinations of bug types and development cycle stages
    combination_percentages = calculate_percentages(stats['combinations'])
    output.append("\n2. Top 5 most frequent combinations of bug types and development cycle stages:")
    for combination, percentage in sorted(combination_percentages.items(), key=lambda x: x[1], reverse=True)[:5]:
        bug_type, development_cycle = combination.split(" + ")
        bug_type_name = BUG_TYPE_LABELS.get(bug_type, "Unknown")
        development_cycle_name = DEVELOPMENT_CYCLE_LABELS.get(development_cycle, "Unknown")
        output.append(f"   {bug_type_name} ({bug_type}) + {development_cycle_name} ({development_cycle}): {percentage:.2f}%")

    # Print to console  
    print("\n".join(output))

    # Save to file
    with open("rq3_analysis_results.txt", "w") as f:
        f.write("\n".join(output))

import matplotlib.pyplot as plt
from matplotlib.cm import get_cmap

def plot_bugs_across_development_phases(stats, output_file):
    development_cycle_data = stats['development_cycle']
    labels = [DEVELOPMENT_CYCLE_LABELS[stage] for stage in development_cycle_data.keys()]
    sizes = list(development_cycle_data.values())
    
    colors = get_cmap('tab20b')(np.linspace(0, 1, len(labels)))
    
    plt.figure(figsize=(12, 8))
    patches, texts, autotexts = plt.pie(sizes, colors=colors, autopct='%1.1f%%', startangle=90, pctdistance=0.85)
    
    for text in texts:
        text.set_text('')
    
    for autotext in autotexts:
        autotext.set_fontsize(16)
    # Create a legend
    plt.legend(patches, labels, title="Development Phases", loc="center left", bbox_to_anchor=(1, 0.5))
    
    plt.axis('equal')
    # plt.title('Distribution of Bugs Across Development Phases', fontsize=16, fontweight='bold')
    
    # Adjust layout to prevent the legend from being cut off
    plt.tight_layout()
    
    plt.savefig(output_file, format='pdf', bbox_inches='tight')
    plt.close()

    print(f"Pie chart saved as {output_file}")

def main():
    file_paths = [
        '../../result/final/labeled_issues_langchain.json',
        '../../result/final/labeled_issues_OpenDevin.json',
        '../../result/final/labeled_issues_autogen.json',
        '../../result/final/labeled_issues_AutoGPT.json',
        '../../result/final/labeled_issues_gpt-engineer.json',
    ]
    
    stats = analyze_json(file_paths)
    print_and_save_rq3_analysis(stats)

    plot_bugs_across_development_phases(stats, 'rq3_bugs_across_development_phases.pdf')

    total_issues = sum(stats['bug_type'].values())
    print(f"\nTotal issues analyzed: {total_issues}")
    print(f"Number of files processed: {len(file_paths)}")

if __name__ == "__main__":
    main()