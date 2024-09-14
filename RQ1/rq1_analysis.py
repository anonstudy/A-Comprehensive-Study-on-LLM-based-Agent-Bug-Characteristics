import json
from collections import Counter, OrderedDict
from typing import Dict, List
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

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

ROOT_CAUSE_LABELS = OrderedDict([
    ("B1", "tool design and behavior mismatch"),
    ("B2", "unsupported tool functionality"),
    ("B3", "unhandled tool exception"),
    ("B4", "model version incompatibility"),
    ("B5", "unhandled model exception handling"),
    ("B6", "api rate limit exceeded"),
    ("B7", "wrong api implementation"),
    ("B8", "improper api usage"),
    ("B9", "misconfigured api keys or tokens"),
    ("B10", "library dependency conflicts"),
    ("B11", "dependency installation failure"),
    ("B12", "incompatible execution environment"),
    ("B13", "unhandled exceptions in asynchronous operations"),
    ("B14", "network connectivity problems"),
    ("B15", "unsupported data format"),
    ("B16", "incorrect response parsing"),
    ("B17", "other")
])

SYMPTOM_LABELS = OrderedDict([
    ("C1", "crash"),
    ("C2", "authentication failure"),
    ("C3", "Wrong Output than expected"),
    ("C4", "performance degradation")
])

def get_label(category: str, value: str) -> str:
    if category == 'bug_type':
        return next((k for k, v in BUG_TYPE_LABELS.items() if v.lower() == value.lower()), "Unknown")
    elif category == 'root_cause':
        return next((k for k, v in ROOT_CAUSE_LABELS.items() if v.lower() == value.lower()), "Unknown")
    elif category == 'symptoms':
        return next((k for k, v in SYMPTOM_LABELS.items() if v.lower() == value.lower()), "Unknown")
    return value

def analyze_json(file_paths: List[str]) -> Dict[str, Counter]:
    categories = ['bug_type', 'root_cause', 'symptoms', 'development_cycle']
    stats = {category: Counter() for category in categories}
    combinations = Counter()

    for file_path in file_paths:
        with open(file_path, 'r') as f:
            data = json.load(f)
            for issue in data.values():
                for category in categories:
                    if category in ['bug_type', 'root_cause', 'symptoms']:
                        label = get_label(category, issue[category])
                        stats[category][label] += 1
                    else:
                        stats[category][issue[category]] += 1

                bug_type_label = get_label('bug_type', issue['bug_type'])
                root_cause_label = get_label('root_cause', issue['root_cause'])
                symptom_label = get_label('symptoms', issue['symptoms'])

                combinations[f"{bug_type_label} + {root_cause_label}"] += 1
                combinations[f"{bug_type_label} + {symptom_label}"] += 1

    stats['combinations'] = combinations
    return stats

def calculate_percentages(counter: Counter) -> Dict[str, float]:
    total = sum(counter.values())
    return {item: (count / total) * 100 for item, count in counter.items()}

def print_and_save_rq1_analysis(stats: Dict[str, Counter]):
    output = []

    # 1. Calculate and print the percentage of each bug type
    bug_type_percentages = calculate_percentages(stats['bug_type'])
    output.append("1. Percentage of each bug type (Bug proportion):")
    for bug_type, percentage in bug_type_percentages.items():
        output.append(f"   {BUG_TYPE_LABELS[bug_type]} ({bug_type}): {percentage:.2f}%")

    # 2. List the top 5 root causes and their percentages
    root_cause_percentages = calculate_percentages(stats['root_cause'])
    output.append("\n2. Top 5 root causes and their percentages:")
    for root_cause, percentage in sorted(root_cause_percentages.items(), key=lambda x: x[1], reverse=True)[:5]:
        label = ROOT_CAUSE_LABELS.get(root_cause, "Unknown")
        if ROOT_CAUSE_LABELS.get(root_cause) == "Unknown":
            print(f"Unknown root cause: {root_cause}")
        output.append(f"   {label} ({root_cause}): {percentage:.2f}%")

    # 3. Calculate and print the percentage of each symptom type
    symptom_percentages = calculate_percentages(stats['symptoms'])
    output.append("\n3. Percentage of each symptom type:")
    for symptom, percentage in symptom_percentages.items():
        # check if symptom exists in SYMPTOM_LABELS
        label = SYMPTOM_LABELS.get(symptom, "Unknown")
        if SYMPTOM_LABELS.get(symptom) == "Unknown":
            print(f"Unknown symptom: {symptom}")
        output.append(f"   {label} ({symptom}): {percentage:.2f}%")

    # 4. Print the top 5 most frequent combinations of bug types and root causes
    combination_percentages = calculate_percentages(stats['combinations'])
    output.append("\n4. Top 5 most frequent combinations of bug types and root causes:")
    for combination, percentage in sorted(combination_percentages.items(), key=lambda x: x[1], reverse=True)[:5]:
        # Split the combination to get individual labels
        bug_type, root_cause = combination.split(" + ")
        bug_type_name = BUG_TYPE_LABELS.get(bug_type, "Unknown")
        root_cause_name = ROOT_CAUSE_LABELS.get(root_cause, "Unknown")
        output.append(f"   {bug_type_name} ({bug_type}) + {root_cause_name} ({root_cause}): {percentage:.2f}%")

    # Print to console
    print("\n".join(output))

    # Save to file
    with open("rq1_analysis_results.txt", "w") as f:
        f.write("\n".join(output))

def plot_bug_distribution_pie(stats: Dict[str, Counter], filename: str):
    plt.figure(figsize=(12, 8))
    
    bug_type_data = stats['bug_type']
    labels = list(bug_type_data.keys())
    sizes = list(bug_type_data.values())
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
    # plt.title('Distribution of Bug Types', fontsize=16)
    
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()

def plot_correlation_heatmap(stats: Dict[str, Counter], filename: str):
    plt.figure(figsize=(12, 8))
    
    bug_types = list(BUG_TYPE_LABELS.keys())
    symptoms = list(SYMPTOM_LABELS.keys())
    
    heatmap_data = np.zeros((len(bug_types), len(symptoms)))
    
    # Calculate the total number of issues
    total_issues = sum(stats['bug_type'].values())
    
    for i, bug in enumerate(bug_types):
        for j, symptom in enumerate(symptoms):
            # Calculate the frequency of each combination
            count = stats['combinations'].get(f"{bug} + {symptom}", 0)
            heatmap_data[i, j] = count / total_issues if total_issues > 0 else 0
    
    sns.heatmap(heatmap_data, xticklabels=symptoms, yticklabels=bug_types, 
                cmap="YlOrRd", annot=True, fmt='.3f', cbar_kws={'label': 'Frequency'})
    
    plt.xlabel('Symptoms', fontsize=14)
    plt.ylabel('Bug Types', fontsize=14)
    
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()

def main():
    file_paths = [
        '../../result/final/labeled_issues_langchain.json',
        '../../result/final/labeled_issues_OpenDevin.json',
        '../../result/final/labeled_issues_autogen.json',
        '../../result/final/labeled_issues_AutoGPT.json',
        '../../result/final/labeled_issues_gpt-engineer.json',
    ]
    
    stats = analyze_json(file_paths)
    print_and_save_rq1_analysis(stats)

    plot_bug_distribution_pie(stats, 'rq1_bug_distribution_pie.pdf')
    plot_correlation_heatmap(stats, 'rq1_bug_symptom_correlation_heatmap.pdf')

    total_issues = sum(stats['bug_type'].values())
    print(f"\nTotal issues analyzed: {total_issues}")
    print(f"Number of files processed: {len(file_paths)}")

if __name__ == "__main__":
    main()