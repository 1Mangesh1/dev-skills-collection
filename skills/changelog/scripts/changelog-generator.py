#!/usr/bin/env python3
"""
Changelog Generator - Automatically generate changelog from git commits
Usage: python3 changelog-generator.py [--version VERSION] [--output CHANGELOG.md]
"""

import re
import subprocess
import argparse
from datetime import datetime
from typing import List, Dict, Tuple

class ChangelogGenerator:
    def __init__(self):
        self.commits = []
        self.categories = {
            'feat': '✨ Features',
            'fix': '🐛 Bug Fixes',
            'docs': '📚 Documentation',
            'style': '🎨 Style',
            'refactor': '♻️ Refactoring',
            'perf': '⚡ Performance',
            'test': '✅ Tests',
            'chore': '🔧 Chore',
            'ci': '🔄 CI/CD'
        }
        self.conventional_commit_pattern = r'^(feat|fix|docs|style|refactor|perf|test|chore|ci)(\(.+\))?!?:\s(.+)'
    
    def get_git_commits(self, from_ref: str = None, to_ref: str = 'HEAD') -> List[Dict]:
        """Extract commits from git history"""
        try:
            if from_ref:
                git_log_cmd = f'git log {from_ref}..{to_ref} --pretty=format:"%H|%an|%ai|%s"'
            else:
                git_log_cmd = f'git log {to_ref} --pretty=format:"%H|%an|%ai|%s"'
            
            result = subprocess.run(git_log_cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"Error: {result.stderr}")
                return []
            
            commits = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    hash_val, author, date, message = line.split('|')
                    commits.append({
                        'hash': hash_val[:7],
                        'author': author,
                        'date': date.split()[0],
                        'message': message
                    })
            
            return commits
        except Exception as e:
            print(f"Error getting commits: {e}")
            return []
    
    def categorize_commit(self, message: str) -> Tuple[str, str]:
        """Categorize commit by conventional commit format"""
        match = re.match(self.conventional_commit_pattern, message)
        
        if match:
            commit_type = match.group(1)
            scope = match.group(2)
            description = match.group(3)
            
            category = self.categories.get(commit_type, 'Other')
            return category, description
        
        return 'Other', message
    
    def group_commits(self, commits: List[Dict]) -> Dict[str, List[Dict]]:
        """Group commits by category"""
        grouped = {}
        
        for commit in commits:
            category, description = self.categorize_commit(commit['message'])
            
            if category not in grouped:
                grouped[category] = []
            
            grouped[category].append({
                **commit,
                'description': description
            })
        
        return grouped
    
    def generate_changelog(self, commits: List[Dict], version: str = None) -> str:
        """Generate changelog content"""
        if not commits:
            return "# Changelog\n\nNo changes found.\n"
        
        grouped = self.group_commits(commits)
        
        changelog = "# Changelog\n\n"
        
        if version:
            changelog += f"## [{version}] - {datetime.now().strftime('%Y-%m-%d')}\n\n"
        else:
            changelog += f"## [Unreleased] - {datetime.now().strftime('%Y-%m-%d')}\n\n"
        
        # Determine order for categories
        category_order = [
            '✨ Features',
            '🐛 Bug Fixes',
            '⚡ Performance',
            '♻️ Refactoring',
            '📚 Documentation',
            '✅ Tests',
            '🔧 Chore',
            '🎨 Style',
            '🔄 CI/CD'
        ]
        
        for category in category_order:
            if category in grouped:
                changelog += f"### {category}\n\n"
                
                for commit in grouped[category]:
                    changelog += f"- {commit['description']} ({commit['hash']})\n"
                
                changelog += "\n"
        
        # Add non-standard categories
        for category in grouped:
            if category not in category_order:
                changelog += f"### {category}\n\n"
                for commit in grouped[category]:
                    changelog += f"- {commit['description']} ({commit['hash']})\n"
                changelog += "\n"
        
        return changelog
    
    def get_latest_tag(self) -> str:
        """Get latest git tag"""
        try:
            result = subprocess.run('git describe --tags --abbrev=0', shell=True, capture_output=True, text=True)
            return result.stdout.strip() if result.returncode == 0 else None
        except:
            return None

def main():
    parser = argparse.ArgumentParser(description='Generate changelog from commits')
    parser.add_argument('--version', help='Version number for this release')
    parser.add_argument('--output', default='CHANGELOG.md', help='Output file path')
    parser.add_argument('--since-tag', action='store_true', help='Generate changelog since last tag')
    parser.add_argument('--all', action='store_true', help='Generate entire changelog')
    
    args = parser.parse_args()
    
    generator = ChangelogGenerator()
    
    # Determine commit range
    if args.since_tag:
        latest_tag = generator.get_latest_tag()
        if latest_tag:
            commits = generator.get_git_commits(from_ref=latest_tag)
            print(f"Commits since {latest_tag}")
        else:
            print("No tags found. Generating changelog for all commits...")
            commits = generator.get_git_commits()
    elif args.all:
        commits = generator.get_git_commits()
    else:
        commits = generator.get_git_commits()
    
    if not commits:
        print("No commits found.")
        return
    
    changelog = generator.generate_changelog(commits, args.version)
    
    # Write to file
    with open(args.output, 'w') as f:
        f.write(changelog)
    
    print(f"Changelog generated: {args.output}")
    print(f"Total commits: {len(commits)}")

if __name__ == '__main__':
    main()
