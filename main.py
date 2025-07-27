
import click
from jira_helper import get_issue, post_comment, add_label
from claude_helper import get_claude_response

@click.command()
@click.argument('ticket_id')
@click.option('--mode', default='summarize', help='Options: summarize, tag, subtasks, test-notes')
def run(ticket_id, mode):
    issue = get_issue(ticket_id)
    summary = issue['fields']['summary']
    description = issue['fields']['description']['content'][0]['content'][0]['text']
    prompt = generate_prompt(mode, summary, description)
    response = get_claude_response(prompt)
    post_comment(ticket_id, response)

    if mode == 'summarize':
        add_label(ticket_id, 'ai-reviewed')

    click.echo(f"✅ {mode.capitalize()} complete for {ticket_id}")

def generate_prompt(mode, summary, description):
    prompts = {
        "summarize": f"""Analyze this Jira ticket and provide:
1. Brief summary (2-3 sentences)
2. Key technical challenges
3. Estimated complexity (Simple/Medium/Complex)
4. Any risks or dependencies

Title: {summary}

Description: {description}""",
        "tag": f"Suggest appropriate Jira tags based on the following issue:\n\n{summary}\n\n{description}",
        "subtasks": f"Break down this issue into smaller development subtasks:\n\n{summary}\n\n{description}",
        "test-notes": f"Generate QA test notes and edge cases:\n\n{summary}\n\n{description}"
    }
    return prompts[mode]

if __name__ == '__main__':
    run()
