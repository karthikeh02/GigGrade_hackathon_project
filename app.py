# import streamlit as st
# from github import Github, Auth
# import git
# import os
# import subprocess
# import pylint.lint
# from radon.complexity import cc_visit
# import coverage
# from pydriller import Repository
# import shutil
# import re

# # Setup with new Auth method

# # Fix: Use new GitHub authentication
# try:
#     auth = Auth.Token(GITHUB_TOKEN)
#     g = Github(auth=auth)
# except:
#     g = Github(GITHUB_TOKEN)  # Fallback for older versions

# # Try importing transformers with fallback
# AI_AVAILABLE = False
# generator = None
# try:
#     from transformers import pipeline
#     import torch
#     generator = pipeline('text-generation', model='distilgpt2', device=-1)
#     AI_AVAILABLE = True
# except Exception as e:
#     pass  # Silent fallback to rule-based

# def generate_ai_summary(metrics_str):
#     """Generate AI summary or fallback to rule-based"""
#     if AI_AVAILABLE and generator:
#         try:
#             prompt = f"Repository analysis: {metrics_str[:512]}. Provide brief summary of strengths/weaknesses, then improvement roadmap."
#             ai_response = generator(prompt, max_length=300, num_return_sequences=1, pad_token_id=50256)[0]['generated_text']
#             summary_match = re.split(r'Roadmap:|improvement|steps', ai_response, flags=re.IGNORECASE, maxsplit=1)
#             summary = summary_match[0].replace(prompt, "").strip()[:300]
#             roadmap_raw = summary_match[1] if len(summary_match) > 1 else ""
#             roadmap = '\n'.join([f"• {line.strip()}" for line in roadmap_raw.splitlines() if line.strip()][:5])
            
#             if not summary or len(summary) < 20:
#                 return generate_rule_based_summary(metrics_str)
#             return summary, roadmap if roadmap else "• Continue current development practices\n• Consider automated testing\n• Expand documentation"
#         except:
#             pass
    
#     return generate_rule_based_summary(metrics_str)

# def generate_rule_based_summary(metrics_str):
#     """Rule-based summary when AI unavailable"""
#     try:
#         scores = eval(metrics_str.split("Scores: ")[1].split(" | ")[0])
#     except:
#         return "Analysis complete. Check detailed scores below.", "• Review code quality\n• Improve documentation\n• Add tests"
    
#     strengths = []
#     weaknesses = []
    
#     if scores['code_quality'] >= 70:
#         strengths.append("high code quality")
#     elif scores['code_quality'] < 50:
#         weaknesses.append("code quality needs improvement")
    
#     if scores['structure'] >= 70:
#         strengths.append("well-organized project structure")
#     elif scores['structure'] < 50:
#         weaknesses.append("project structure could be better organized")
    
#     if scores['documentation'] >= 70:
#         strengths.append("comprehensive documentation")
#     elif scores['documentation'] < 50:
#         weaknesses.append("documentation needs enhancement")
    
#     if scores['tests'] >= 60:
#         strengths.append("good test coverage")
#     elif scores['tests'] < 40:
#         weaknesses.append("test coverage is insufficient")
    
#     summary_parts = []
#     if strengths:
#         summary_parts.append(f"✓ Strengths: {', '.join(strengths)}")
#     if weaknesses:
#         summary_parts.append(f"⚠ Areas for improvement: {', '.join(weaknesses)}")
    
#     summary = ". ".join(summary_parts) if summary_parts else "Repository shows average quality indicators across metrics."
    
#     roadmap_items = []
#     if scores['tests'] < 60:
#         roadmap_items.append("• Add comprehensive unit tests (target 80%+ coverage)")
#     if scores['documentation'] < 60:
#         roadmap_items.append("• Enhance README with clear installation and usage instructions")
#     if scores['code_quality'] < 60:
#         roadmap_items.append("• Refactor complex code sections for better maintainability")
#     if scores['version_control'] < 50:
#         roadmap_items.append("• Adopt feature branch workflow with pull requests")
#     if scores['structure'] < 60:
#         roadmap_items.append("• Reorganize into standard project layout (src/, tests/, docs/)")
    
#     if not roadmap_items:
#         roadmap_items = [
#             "• Maintain current code quality standards",
#             "• Implement CI/CD pipeline for automated testing",
#             "• Add contribution guidelines for collaborators"
#         ]
    
#     return summary, '\n'.join(roadmap_items[:5])

# # UI
# st.set_page_config(page_title="GitGrade", page_icon="🎯", layout="wide")
# st.title("🎯 GitGrade: AI Repository Analyzer")
# st.caption("Comprehensive GitHub repository analysis with automated scoring")

# # Check token validity
# token_valid = False
# try:
#     g.get_user().login
#     token_valid = True
# except:
#     st.error("⚠️ GitHub Token Invalid! Generate new token at: https://github.com/settings/tokens")
#     st.info("Required scopes: `repo` (for private repos) or `public_repo` (for public only)")
#     st.stop()

# repo_url = st.text_input("🔗 Enter Public GitHub Repository URL", 
#                           placeholder="https://github.com/username/repository",
#                           help="Paste the full URL of any public GitHub repository")

# if st.button("🚀 Analyze Repository", type="primary", use_container_width=True):
#     if not repo_url:
#         st.error("Please enter a repository URL")
#     else:
#         try:
#             # Parse repo
#             if "github.com/" not in repo_url:
#                 st.error("Invalid GitHub URL. Use format: https://github.com/username/repo")
#                 st.stop()
            
#             repo_path = repo_url.split("github.com/")[1].strip("/").split("?")[0]
            
#             with st.spinner(f"🔍 Analyzing repository..."):
#                 try:
#                     repo = g.get_repo(repo_path)
#                 except Exception as e:
#                     st.error(f"❌ Cannot access repository: {str(e)}")
#                     st.info("Make sure:\n- Repository is public\n- URL is correct\n- Repository exists")
#                     st.stop()
                
#                 # Gather metadata
#                 try:
#                     languages = repo.get_languages()
#                     has_readme = any(f.path.upper() == "README.MD" for f in repo.get_contents(""))
#                     branches = len(list(repo.get_branches()))
#                     prs = repo.get_pulls(state='all').totalCount
#                 except:
#                     branches = 1
#                     prs = 0
#                     languages = {}
#                     has_readme = False

#                 # Clone and analyze
#                 clone_dir = "temp_repo"
#                 shutil.rmtree(clone_dir, ignore_errors=True)
                
#                 try:
#                     git.Repo.clone_from(repo.clone_url, clone_dir, depth=1)
#                 except:
#                     st.error("Failed to clone repository. Check network connection.")
#                     st.stop()

#                 # Analyze code
#                 pylint_scores = []
#                 complexity_scores = []
#                 py_files_count = 0
                
#                 for root, _, files in os.walk(clone_dir):
#                     for file in files:
#                         if file.endswith(".py"):
#                             py_files_count += 1
#                             filepath = os.path.join(root, file)
                            
#                             # Pylint
#                             try:
#                                 result = pylint.lint.Run([filepath], do_exit=False)
#                                 if hasattr(result.linter, 'stats') and hasattr(result.linter.stats, 'global_note'):
#                                     pylint_scores.append(result.linter.stats.global_note)
#                             except:
#                                 pass
                            
#                             # Complexity
#                             try:
#                                 with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
#                                     code = f.read()
#                                 blocks = cc_visit(code)
#                                 complexity_scores.extend([b.complexity for b in blocks])
#                             except:
#                                 pass

#                 avg_pylint = sum(pylint_scores) / len(pylint_scores) if pylint_scores else 5
#                 avg_complexity = sum(complexity_scores) / len(complexity_scores) if complexity_scores else 5

#                 has_good_structure = any(d in os.listdir(clone_dir) for d in ["src", "tests", "docs", "lib"])

#                 # Coverage (quick check)
#                 coverage_percent = 0
#                 try:
#                     original_dir = os.getcwd()
#                     os.chdir(clone_dir)
#                     result = subprocess.run(["coverage", "run", "-m", "pytest"], 
#                                           capture_output=True, check=False, timeout=30)
#                     if result.returncode == 0:
#                         cov = coverage.Coverage()
#                         cov.load()
#                         coverage_percent = cov.report()
#                     os.chdir(original_dir)
#                 except:
#                     try:
#                         os.chdir(original_dir)
#                     except:
#                         pass

#                 # README quality
#                 readme_quality = 0
#                 if has_readme:
#                     try:
#                         readme_files = [f for f in os.listdir(clone_dir) if f.upper().startswith("README")]
#                         if readme_files:
#                             with open(os.path.join(clone_dir, readme_files[0]), 'r', encoding='utf-8', errors='ignore') as f:
#                                 content = f.read()
#                             readme_quality = min(100, 
#                                 (25 if len(content) > 500 else 10) +
#                                 (25 if "install" in content.lower() else 0) +
#                                 (25 if "usage" in content.lower() or "example" in content.lower() else 0) +
#                                 (25 if content.count("#") >= 3 else 0))
#                     except:
#                         readme_quality = 20

#                 # Get commits
#                 try:
#                     commits = list(Repository(repo.clone_url, only_no_merge=True).traverse_commits())
#                     commit_count = len(commits)
#                     if commit_count > 1:
#                         days = (commits[-1].committer_date - commits[0].committer_date).days or 1
#                         commit_consistency = min(100, (commit_count / days) * 100)
#                     else:
#                         commit_consistency = 50
#                 except:
#                     commit_count = repo.get_commits().totalCount
#                     commit_consistency = min(100, commit_count)

#                 relevance = min((repo.stargazers_count * 3 + repo.forks_count * 5), 100)

#                 # Cleanup
#                 shutil.rmtree(clone_dir, ignore_errors=True)

#                 # Calculate scores
#                 scores = {
#                     "code_quality": min(100, avg_pylint * 10) if py_files_count > 0 else 50,
#                     "structure": 85 if has_good_structure else 35,
#                     "documentation": readme_quality,
#                     "tests": min(100, coverage_percent) if coverage_percent > 0 else (30 if py_files_count > 0 else 50),
#                     "community": min(100, relevance),
#                     "activity": min(100, commit_consistency),
#                     "collaboration": min(100, (35 if branches > 1 else 0) + (35 if prs > 5 else prs * 7))
#                 }
#                 total_score = sum(scores.values()) / len(scores)

#                 # Generate summary
#                 metrics_str = f"Scores: {scores} | Languages: {languages} | Commits: {commit_count} | Stars: {repo.stargazers_count} | Forks: {repo.forks_count}"
                
#                 summary, roadmap = generate_ai_summary(metrics_str)

#                 # Display results
#                 st.success(f"✅ Analysis Complete: **{repo.full_name}**")
                
#                 # Score cards
#                 cols = st.columns(4)
#                 with cols[0]:
#                     st.metric("Overall Score", f"{int(total_score)}/100", 
#                              delta="Excellent" if total_score >= 80 else "Good" if total_score >= 60 else "Needs Work")
#                 with cols[1]:
#                     st.metric("Code Quality", f"{int(scores['code_quality'])}/100")
#                 with cols[2]:
#                     st.metric("Documentation", f"{int(scores['documentation'])}/100")
#                 with cols[3]:
#                     st.metric("Activity", f"{int(scores['activity'])}/100")

#                 # Detailed scores
#                 st.subheader("📊 Detailed Category Scores")
#                 for key, value in scores.items():
#                     color = "🟢" if value >= 70 else "🟡" if value >= 50 else "🔴"
#                     st.progress(min(value / 100, 1.0), text=f"{color} {key.replace('_', ' ').title()}: {int(value)}/100")

#                 # Summary
#                 st.subheader("📝 AI Analysis Summary")
#                 st.info(summary)

#                 # Roadmap
#                 st.subheader("🗺️ Recommended Improvement Roadmap")
#                 st.markdown(roadmap)

#                 # Detailed metrics
#                 with st.expander("🔍 View Detailed Metrics"):
#                     col1, col2 = st.columns(2)
#                     with col1:
#                         st.json({
#                             "repository": repo.full_name,
#                             "languages": languages,
#                             "total_commits": commit_count,
#                             "branches": branches,
#                             "pull_requests": prs,
#                         })
#                     with col2:
#                         st.json({
#                             "stars": repo.stargazers_count,
#                             "forks": repo.forks_count,
#                             "watchers": repo.watchers_count,
#                             "open_issues": repo.open_issues_count,
#                             "avg_pylint_score": round(avg_pylint, 2) if pylint_scores else "N/A",
#                             "avg_complexity": round(avg_complexity, 2) if complexity_scores else "N/A",
#                         })

#         except Exception as e:
#             st.error(f"❌ Error during analysis: {str(e)}")
#             with st.expander("Debug Information"):
#                 st.code(str(e))
#                 st.info("Common issues:\n- Invalid repository URL\n- Network connection problems\n- Missing dependencies")

# # Footer
# st.markdown("---")
# st.caption("💡 Tip: For best results, analyze repositories with Python code and documentation")










import streamlit as st
from github import Github, Auth
import git
import os
from radon.complexity import cc_visit
import shutil
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup with new Auth method - works both locally and on Streamlit Cloud
try:
    # Try Streamlit secrets first (for deployment)
    GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
except:
    # Fall back to .env file (for local development)
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    if not GITHUB_TOKEN:
        st.error("⚠️ GitHub token not found! Add it to .env file or Streamlit secrets")
        st.stop()

# Fix: Use new GitHub authentication
try:
    auth = Auth.Token(GITHUB_TOKEN)
    g = Github(auth=auth)
except:
    g = Github(GITHUB_TOKEN)

# Try importing transformers with fallback
AI_AVAILABLE = False
generator = None
try:
    from transformers import pipeline
    import torch
    generator = pipeline('text-generation', model='distilgpt2', device=-1)
    AI_AVAILABLE = True
except:
    pass

def generate_ai_summary(metrics_str):
    """Generate AI summary or fallback to rule-based"""
    if AI_AVAILABLE and generator:
        try:
            prompt = f"Repository analysis: {metrics_str[:512]}. Provide brief summary of strengths/weaknesses, then improvement roadmap."
            ai_response = generator(prompt, max_length=300, num_return_sequences=1, pad_token_id=50256)[0]['generated_text']
            summary_match = re.split(r'Roadmap:|improvement|steps', ai_response, flags=re.IGNORECASE, maxsplit=1)
            summary = summary_match[0].replace(prompt, "").strip()[:300]
            roadmap_raw = summary_match[1] if len(summary_match) > 1 else ""
            roadmap = '\n'.join([f"• {line.strip()}" for line in roadmap_raw.splitlines() if line.strip()][:5])
            
            if not summary or len(summary) < 20:
                return generate_rule_based_summary(metrics_str)
            return summary, roadmap if roadmap else "• Continue current development practices\n• Consider automated testing\n• Expand documentation"
        except:
            pass
    
    return generate_rule_based_summary(metrics_str)

def generate_rule_based_summary(metrics_str):
    """Rule-based summary when AI unavailable"""
    try:
        scores = eval(metrics_str.split("Scores: ")[1].split(" | ")[0])
    except:
        return "Analysis complete. Check detailed scores below.", "• Review code quality\n• Improve documentation\n• Add tests"
    
    strengths = []
    weaknesses = []
    
    if scores['code_quality'] >= 70:
        strengths.append("high code quality")
    elif scores['code_quality'] < 50:
        weaknesses.append("code quality needs improvement")
    
    if scores['structure'] >= 70:
        strengths.append("well-organized project structure")
    elif scores['structure'] < 50:
        weaknesses.append("project structure could be better organized")
    
    if scores['documentation'] >= 70:
        strengths.append("comprehensive documentation")
    elif scores['documentation'] < 50:
        weaknesses.append("documentation needs enhancement")
    
    if scores['tests'] >= 60:
        strengths.append("good test coverage")
    elif scores['tests'] < 40:
        weaknesses.append("test coverage is insufficient")
    
    summary_parts = []
    if strengths:
        summary_parts.append(f"✓ Strengths: {', '.join(strengths)}")
    if weaknesses:
        summary_parts.append(f"⚠ Areas for improvement: {', '.join(weaknesses)}")
    
    summary = ". ".join(summary_parts) if summary_parts else "Repository shows average quality indicators across metrics."
    
    roadmap_items = []
    if scores['tests'] < 60:
        roadmap_items.append("• Add comprehensive unit tests (target 80%+ coverage)")
    if scores['documentation'] < 60:
        roadmap_items.append("• Enhance README with clear installation and usage instructions")
    if scores['code_quality'] < 60:
        roadmap_items.append("• Refactor complex code sections for better maintainability")
    if scores['version_control'] < 50:
        roadmap_items.append("• Adopt feature branch workflow with pull requests")
    if scores['structure'] < 60:
        roadmap_items.append("• Reorganize into standard project layout (src/, tests/, docs/)")
    
    if not roadmap_items:
        roadmap_items = [
            "• Maintain current code quality standards",
            "• Implement CI/CD pipeline for automated testing",
            "• Add contribution guidelines for collaborators"
        ]
    
    return summary, '\n'.join(roadmap_items[:5])

def analyze_python_file(filepath):
    """Analyze a single Python file for complexity"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            code = f.read()
        blocks = cc_visit(code)
        return [b.complexity for b in blocks]
    except:
        return []

# UI
st.set_page_config(page_title="GitGrade", page_icon="🎯", layout="wide")
st.title("🎯 GitGrade: AI Repository Analyzer")
st.caption("⚡ Lightning-fast comprehensive GitHub analysis")

# Check token validity
token_valid = False
try:
    g.get_user().login
    token_valid = True
except:
    st.error("⚠️ GitHub Token Invalid! Generate new token at: https://github.com/settings/tokens")
    st.info("Required scopes: `public_repo` for public repositories")
    st.stop()

# Sidebar for quick examples
with st.sidebar:
    st.header("🚀 Quick Examples")
    examples = {
        "Flask (Fast)": "https://github.com/pallets/flask",
        "Requests (Fast)": "https://github.com/psf/requests",
        "Django (Medium)": "https://github.com/django/django",
        "Streamlit": "https://github.com/streamlit/streamlit"
    }
    for name, url in examples.items():
        if st.button(name, use_container_width=True):
            st.session_state['repo_url'] = url

repo_url = st.text_input("🔗 Enter Public GitHub Repository URL", 
                          value=st.session_state.get('repo_url', ''),
                          placeholder="https://github.com/username/repository",
                          help="Paste the full URL of any public GitHub repository")

if st.button("🚀 Analyze Repository", type="primary", use_container_width=True):
    if not repo_url:
        st.error("Please enter a repository URL")
    else:
        start_time = time.time()
        try:
            if "github.com/" not in repo_url:
                st.error("Invalid GitHub URL. Use format: https://github.com/username/repo")
                st.stop()
            
            repo_path = repo_url.split("github.com/")[1].strip("/").split("?")[0]
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Step 1: Fetch repo metadata (15%)
            status_text.text("📡 Fetching repository metadata...")
            progress_bar.progress(15)
            
            try:
                repo = g.get_repo(repo_path)
            except Exception as e:
                error_msg = str(e)
                st.error(f"❌ Cannot access repository")
                
                if "404" in error_msg:
                    st.warning("**Repository not found!**")
                    st.info("• The repository doesn't exist\n• It's private (needs `repo` scope)\n• URL is misspelled")
                st.stop()
            
            # Gather basic metadata quickly
            languages = repo.get_languages()
            stars = repo.stargazers_count
            forks = repo.forks_count
            open_issues = repo.open_issues_count
            
            # Step 2: Check structure (25%)
            status_text.text("🔍 Analyzing repository structure...")
            progress_bar.progress(25)
            
            try:
                contents = repo.get_contents("")
                has_readme = any(f.path.upper() == "README.MD" for f in contents)
                has_tests = any(f.path.lower() in ["tests", "test"] for f in contents if f.type == "dir")
                has_src = any(f.path.lower() in ["src", "lib"] for f in contents if f.type == "dir")
                has_docs = any(f.path.lower() == "docs" for f in contents if f.type == "dir")
            except:
                has_readme = has_tests = has_src = has_docs = False
            
            has_good_structure = sum([has_tests, has_src, has_docs]) >= 2
            
            # Step 3: Analyze branches/PRs (35%)
            status_text.text("🌿 Checking version control...")
            progress_bar.progress(35)
            
            try:
                branches = repo.get_branches().totalCount
                prs = repo.get_pulls(state='all').totalCount
            except:
                branches = 1
                prs = 0
            
            # Step 4: Clone (shallow) for code analysis (50%)
            status_text.text("📥 Cloning repository (shallow)...")
            progress_bar.progress(50)
            
            clone_dir = "temp_repo"
            shutil.rmtree(clone_dir, ignore_errors=True)
            
            try:
                # Shallow clone - only latest commit, much faster!
                git.Repo.clone_from(repo.clone_url, clone_dir, depth=1, single_branch=True)
            except:
                st.error("Failed to clone repository")
                st.stop()

            # Step 5: Analyze Python files (75%)
            status_text.text("🐍 Analyzing Python code quality...")
            progress_bar.progress(75)
            
            py_files = []
            for root, _, files in os.walk(clone_dir):
                if '/.git' in root or '/venv' in root or '/node_modules' in root:
                    continue
                for file in files:
                    if file.endswith(".py"):
                        py_files.append(os.path.join(root, file))
            
            py_files_count = len(py_files)
            
            # Limit analysis to first 50 files for speed
            files_to_analyze = py_files[:50]
            
            complexity_scores = []
            if files_to_analyze:
                # Parallel processing for speed
                with ThreadPoolExecutor(max_workers=4) as executor:
                    futures = {executor.submit(analyze_python_file, f): f for f in files_to_analyze}
                    for future in as_completed(futures):
                        complexity_scores.extend(future.result())
            
            avg_complexity = sum(complexity_scores) / len(complexity_scores) if complexity_scores else 5
            
            # Quick code quality heuristic (no pylint - too slow!)
            code_quality_score = 100 - min(50, (avg_complexity - 1) * 10)
            
            # Step 6: Check README (85%)
            status_text.text("📄 Evaluating documentation...")
            progress_bar.progress(85)
            
            readme_quality = 0
            if has_readme:
                try:
                    readme_files = [f for f in os.listdir(clone_dir) if f.upper().startswith("README")]
                    if readme_files:
                        with open(os.path.join(clone_dir, readme_files[0]), 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        readme_quality = min(100, 
                            (25 if len(content) > 500 else 10) +
                            (25 if "install" in content.lower() else 0) +
                            (25 if "usage" in content.lower() or "example" in content.lower() else 0) +
                            (25 if content.count("#") >= 3 else 0))
                except:
                    readme_quality = 20
            
            # Step 7: Get commit data (95%)
            status_text.text("📊 Calculating final scores...")
            progress_bar.progress(95)
            
            try:
                # Quick commit count (no full history traversal)
                commit_count = min(repo.get_commits().totalCount, 1000)  # Cap for speed
                
                # Estimate activity from commit count
                if commit_count > 500:
                    commit_consistency = 90
                elif commit_count > 100:
                    commit_consistency = 70
                elif commit_count > 20:
                    commit_consistency = 50
                else:
                    commit_consistency = 30
            except:
                commit_count = 1
                commit_consistency = 30
            
            relevance = min((stars * 3 + forks * 5), 100)
            
            # Cleanup
            shutil.rmtree(clone_dir, ignore_errors=True)
            
            # Calculate scores
            scores = {
                "code_quality": code_quality_score if py_files_count > 0 else 50,
                "structure": 85 if has_good_structure else 35,
                "documentation": readme_quality,
                "tests": 70 if has_tests else 20,
                "community": min(100, relevance),
                "activity": commit_consistency,
                "collaboration": min(100, (35 if branches > 1 else 0) + (35 if prs > 5 else prs * 7))
            }
            total_score = sum(scores.values()) / len(scores)
            
            # Generate summary
            metrics_str = f"Scores: {scores} | Languages: {languages} | Commits: {commit_count} | Stars: {stars} | Forks: {forks}"
            
            summary, roadmap = generate_ai_summary(metrics_str)
            
            # Complete!
            progress_bar.progress(100)
            status_text.empty()
            progress_bar.empty()
            
            elapsed_time = time.time() - start_time
            
            # Display results
            st.success(f"✅ Analysis Complete: **{repo.full_name}** (⚡ {elapsed_time:.1f}s)")
            
            # Score cards
            cols = st.columns(4)
            with cols[0]:
                st.metric("Overall Score", f"{int(total_score)}/100", 
                         delta="Excellent" if total_score >= 80 else "Good" if total_score >= 60 else "Needs Work")
            with cols[1]:
                st.metric("Code Quality", f"{int(scores['code_quality'])}/100")
            with cols[2]:
                st.metric("Documentation", f"{int(scores['documentation'])}/100")
            with cols[3]:
                st.metric("Activity", f"{int(scores['activity'])}/100")

            # Detailed scores
            st.subheader("📊 Detailed Category Scores")
            for key, value in scores.items():
                color = "🟢" if value >= 70 else "🟡" if value >= 50 else "🔴"
                st.progress(min(value / 100, 1.0), text=f"{color} {key.replace('_', ' ').title()}: {int(value)}/100")

            # Summary
            st.subheader("📝 Analysis Summary")
            st.info(summary)

            # Roadmap
            st.subheader("🗺️ Recommended Improvement Roadmap")
            st.markdown(roadmap)

            # Detailed metrics
            with st.expander("🔍 View Detailed Metrics"):
                col1, col2 = st.columns(2)
                with col1:
                    st.json({
                        "repository": repo.full_name,
                        "languages": languages,
                        "python_files": py_files_count,
                        "total_commits": commit_count,
                        "branches": branches,
                        "pull_requests": prs,
                    })
                with col2:
                    st.json({
                        "stars": stars,
                        "forks": forks,
                        "watchers": repo.watchers_count,
                        "open_issues": open_issues,
                        "avg_complexity": round(avg_complexity, 2) if complexity_scores else "N/A",
                        "has_tests_dir": has_tests,
                        "has_docs_dir": has_docs,
                    })
                    
            st.balloons()

        except Exception as e:
            st.error(f"❌ Error during analysis: {str(e)}")
            with st.expander("Debug Information"):
                st.code(str(e))

# Footer
st.markdown("---")
st.caption("⚡ Optimized for speed | 💡 Analyzes up to 50 Python files | 🚀 Shallow git clone")