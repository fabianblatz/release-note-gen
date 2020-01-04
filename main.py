#!/usr/bin/env python
# -*- coding: utf-8 -*-
from git import Repo
import os
import argparse
import re
import collections
import sys

def collect_commits(path, since, until):
    repo = Repo(path)
    print("Analyzing repo {}".format(os.path.basename(repo.working_dir)))
    return repo.iter_commits('{}..{}'.format(since, until))

def build_issue_dict(commits, project):
    issues = collections.defaultdict(list)
    regex = re.compile("(\S*({}-[0-9]+)\S*)".format(project), re.IGNORECASE)
    for commit in commits:
        #remove merge commits
        if "Merged" in commit.message or "Merge" in commit.message:
            continue
        
        match = regex.search(commit.message)
        if match is not None:
            issue_nr = match.group(2)
            if issue_nr not in issues:
                print("Found refrenced jira issue {}".format(issue_nr))
            issues[issue_nr].append(commit.message.replace(match.group(1), "").strip().split('\n', 1)[0])
        else:
            issues['misc'].append(commit.message.strip().split('\n', 1)[0])
    return issues 

def build_notes(commit_dict):
    template = "{key} - {message}"
    res=""
    with open("commit.template","r+") as f:
        template=f.readline()
    for k in commit_dict:
        messages = commit_dict[k]
        message_buf = "; ".join(messages)
        if 'misc' == k:
            res+= "* Miscellaneous: " + message_buf +"\n"
        else:
            res+=template.format(key=k, message=message_buf)+"\n"
    return res

if __name__ == "__main__":
    reload(sys)  
    sys.setdefaultencoding('utf-8')
    parser = argparse.ArgumentParser()
    parser.add_argument("-V", "--version", help="show program version", action="store_true")
    parser.add_argument("-p", "--project", help="jira project key")
    parser.add_argument("-r", "--repo", help="path to repository")
    parser.add_argument("-s", "--since", help="tag or commit since commits will be watched")
    parser.add_argument("-u", "--until", help="tag or commit until commits will be watched")

    args = parser.parse_args()
    if not args.repo:
        print("provide a repo you -.-")    
        exit(1);
    if not args.project:
        print("provide a jira issue project key")
    
    commits = collect_commits(args.repo, args.since, args.until)
    issue_dict = build_issue_dict(commits, args.project)
    notes = build_notes(issue_dict)
    print("---------------------------------------------------------")
    print("Writing to release-notes.txt")
    with open("release-notes.txt", "w+") as f:
        f.write(notes)
