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

def analyze_json(file_path: str) -> Dict[str, Counter]:
    categories = ['bug_type', 'root_cause', 'symptoms']
    stats = {category: Counter() for category in categories}
    combinations = Counter()

    with open(file_path, 'r') as f:
        data = json.load(f)
        for issue in data.values():
            for category in categories:
                label = get_label(category, issue[category])
                stats[category][label] += 1

            bug_type_label = get_label('bug_type', issue['bug_type'])
            root_cause_label = get_label('root_cause', issue['root_cause'])

            combinations[f"{bug_type_label} + {root_cause_label}"] += 1

    stats['combinations'] = combinations
    return stats

def calculate_percentages(counter: Counter) -> Dict[str, float]:
    total = sum(counter.values())
    return {item: (count / total) * 100 for item, count in counter.items()}

def print_and_save_rq2_analysis(framework_stats: Dict[str, Dict[str, Counter]]):
    output = []

    for framework, stats in framework_stats.items():
        output.append(f"Analysis for {framework}:")

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
            label = SYMPTOM_LABELS.get(symptom, "Unknown")
            if SYMPTOM_LABELS.get(symptom) == "Unknown":
                print(f"Unknown symptom: {symptom}")
            output.append(f"   {label} ({symptom}): {percentage:.2f}%")

        # 4. Print the top 5 most frequent combinations of bug types and root causes
        combination_percentages = calculate_percentages(stats['combinations'])
        output.append("\n4. Top 5 most frequent combinations of bug types and root causes:")
        for combination, percentage in sorted(combination_percentages.items(), key=lambda x: x[1], reverse=True)[:5]:
            bug_type, root_cause = combination.split(" + ")
            bug_type_name = BUG_TYPE_LABELS.get(bug_type, "Unknown")
            root_cause_name = ROOT_CAUSE_LABELS.get(root_cause, "Unknown")
            output.append(f"   {bug_type_name} ({bug_type}) + {root_cause_name} ({root_cause}): {percentage:.2f}%")

        output.append("\n")

    # Print to console
    print("\n".join(output))

    # Save to file
    with open("rq2_analysis_results.txt", "w") as f:
        f.write("\n".join(output))

def plot_bug_types_across_frameworks(framework_stats: Dict[str, Dict[str, Counter]], filename: str):
    frameworks = list(framework_stats.keys())
    bug_types = list(BUG_TYPE_LABELS.keys())
    
    data = np.zeros((len(bug_types), len(frameworks)))
    for i, framework in enumerate(frameworks):
        for j, bug_type in enumerate(bug_types):
            data[j, i] = framework_stats[framework]['bug_type'].get(bug_type, 0)
    
    # Convert to percentages
    data_percentage = data / data.sum(axis=0) * 100
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    bottom = np.zeros(len(frameworks))
    for i, bug_type in enumerate(bug_types):
        ax.bar(frameworks, data_percentage[i], bottom=bottom, label=f"{bug_type}: {BUG_TYPE_LABELS[bug_type]}")
        bottom += data_percentage[i]
    
    ax.set_title('Distribution of Bug Types Across Frameworks', fontsize=16)
    # ax.set_xlabel('Frameworks', fontsize=12)
    ax.set_ylabel('Percentage', fontsize=16)
    ax.legend(title='Bug Types', bbox_to_anchor=(1.05, 1), loc='upper left')
    
    plt.xticks(rotation=45, ha='right', fontsize=16)
    plt.tight_layout()
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()

def main():
    file_paths = {
        'langchain': '../../result/final/labeled_issues_langchain.json',
        'OpenDevin': '../../result/final/labeled_issues_OpenDevin.json',
        'autogen': '../../result/final/labeled_issues_autogen.json',
        'AutoGPT': '../../result/final/labeled_issues_AutoGPT.json',
        'gpt-engineer': '../../result/final/labeled_issues_gpt-engineer.json',
    }
    
    framework_stats = {}
    for framework, file_path in file_paths.items():
        framework_stats[framework] = analyze_json(file_path)

    # print_and_save_rq2_analysis(framework_stats)
    
    plot_bug_types_across_frameworks(framework_stats, 'rq2_bug_types_across_frameworks.pdf')

if __name__ == "__main__":
    main()