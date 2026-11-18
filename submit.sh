#!/usr/bin/env bash
# Checks your work, saves everything AppCreative needs, and submits it.
cd "$(dirname "$0")" || exit 1
mkdir -p submission

stop() { echo; echo "❌ $1"; echo "Nothing was submitted. Fix that and run 'bash submit.sh' again."; exit 1; }

echo "Getting your submission ready..."
echo

# 1. The clock
[ -f submission/started_at.txt ] || stop "The clock was never started. Run 'bash begin.sh' (you should have done this at the start)."

# 2. Written answers
if grep -q "_Write your answer here._" ANSWERS.md; then
  stop "ANSWERS.md still has unanswered questions."
fi
echo "✅ Written answers found"

# 3. AI chat history
chat_files=$(find submission -maxdepth 1 -type f ! -name "*.txt" ! -name "*.diff" | wc -l)
if [ "$chat_files" -eq 0 ]; then
  echo "⚠️  No AI chat history found in the submission folder."
  echo "   In Copilot Chat, open the ... menu (or press F1 and type 'Export Chat')"
  echo "   and save it into the 'submission' folder. If you can't export it,"
  echo "   copy the whole conversation into a new file called submission/ai-chat.md."
  read -r -p "   Submit without your AI chat history? (y/N) " answer
  [ "$answer" = "y" ] || [ "$answer" = "Y" ] || stop "Add your AI chat history first."
else
  echo "✅ AI chat history found"
fi

# 4. Recording link
echo
read -r -p "Paste the link to your screen recording: " video
case "$video" in
  http*) echo "$video" > submission/video-link.txt; echo "✅ Recording link saved" ;;
  *) stop "That doesn't look like a link. It should start with http." ;;
esac

# 5. Finish time and the health check
date -u +"%Y-%m-%dT%H:%M:%SZ" > submission/finished_at.txt
echo
echo "Running the health check (about 30 seconds)..."
bash start.sh >/dev/null 2>&1
bash check.sh
cp check-results.txt submission/check-results.txt 2>/dev/null

# 6. A record of everything you changed
first_commit=$(git rev-list --max-parents=0 HEAD | tail -1)
git add -A
git diff --cached "$first_commit" > submission/changes.diff
git add -A

# 7. Submit
if ! git diff --cached --quiet; then
  git commit -q -m "Submission" || stop "Couldn't save your work with git."
fi
if git push -q; then
  echo
  echo "✅ Submitted at $(cat submission/finished_at.txt) (UTC)."
  echo "Started at      $(cat submission/started_at.txt) (UTC)."
  echo
  echo "Make sure AppCreative-dev is a collaborator on this repository"
  echo "(Settings → Collaborators), then let your AppCreative contact know you're done."
else
  stop "Couldn't upload to GitHub. Check your internet connection and try again."
fi
