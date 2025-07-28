import click
from jira_helper import get_issue, post_comment, add_label
from claude_helper import get_claude_response

def extract_text_from_content(content):
    """Recursively extract text from Jira's Atlassian Document Format"""
    if isinstance(content, str):
        return content
    
    text_parts = []
    
    if isinstance(content, dict):
        # Handle text nodes
        if content.get('type') == 'text':
            text_parts.append(content.get('text', ''))
        
        # Handle mentions
        elif content.get('type') == 'mention':
            attrs = content.get('attrs', {})
            text_parts.append(attrs.get('text', ''))
        
        # Handle nested content
        if 'content' in content:
            for item in content['content']:
                text_parts.append(extract_text_from_content(item))
    
    elif isinstance(content, list):
        for item in content:
            text_parts.append(extract_text_from_content(item))
    
    return ' '.join(filter(None, text_parts))

@click.command()
@click.argument('ticket_id')
@click.option('--mode', default='summarize', help='Options: summarize, tag, subtasks, test-notes')
def run(ticket_id, mode):
    issue = get_issue(ticket_id)
    summary = issue['fields'].get('summary', 'No summary')
    
    # Extract description text
    description_obj = issue['fields'].get('description')
    if description_obj is None:
        description = "No description provided"
    else:
        description = extract_text_from_content(description_obj)
    
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