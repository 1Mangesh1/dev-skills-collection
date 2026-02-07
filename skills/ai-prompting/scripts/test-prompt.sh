#!/bin/bash
# Prompt Testing Suite - Test prompts against different models
# Helps evaluate which prompting technique works best for a task

usage() {
    echo "Usage: test-prompt.sh '<prompt>' [technique]"
    echo "Techniques: basic, fewshot, cot, structured"
    exit 1
}

if [ $# -lt 1 ]; then
    usage
fi

PROMPT="$1"
TECHNIQUE="${2:-basic}"

# Apply technique transformations
case "$TECHNIQUE" in
    basic)
        FINAL_PROMPT="$PROMPT"
        ;;
    fewshot)
        FINAL_PROMPT="Consider these examples first:\n[Example 1: ...]\n[Example 2: ...]\n\nNow: $PROMPT"
        ;;
    cot)
        FINAL_PROMPT="Let's think step by step:\n1. Understand the problem\n2. Break it down\n3. Reason through\n4. Conclude\n\n$PROMPT"
        ;;
    structured)
        FINAL_PROMPT="Please structure your response as:\n- Title\n- Key points\n- Examples\n- Summary\n\n$PROMPT"
        ;;
    *)
        echo "Unknown technique: $TECHNIQUE"
        usage
        ;;
esac

echo "Testing with $TECHNIQUE technique..."
echo "========================================"
echo -e "$FINAL_PROMPT"
echo "========================================"
echo "Copy this prompt to Claude/ChatGPT for testing."
