import click
from jira_helper import get_issue, post_comment, add_label
from claude_helper import get_claude_response
# from rca_generator import generate_rca, format_rca_as_markdown, save_rca_to_file, format_rca_for_jira

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
@click.option('--mode', default='summarize', help='Options: summarize, tag, subtasks, test-notes, rca')
@click.option('--post-rca/--no-post-rca', default=None, help='Post RCA to Jira without prompting (RCA mode only)')
def run(ticket_id, mode, post_rca):
    # Enhanced visual output
    mode_icons = {
        'summarize': '📋',
        'tag': '🏷️',
        'subtasks': '📝',
        'test-notes': '🧪',
        'rca': '🔍'
    }
    
    mode_names = {
        'summarize': 'ANALYSIS',
        'tag': 'TAGGING',
        'subtasks': 'TASK BREAKDOWN', 
        'test-notes': 'QA TEST PLAN',
        'rca': 'ROOT CAUSE ANALYSIS'
    }
    
    icon = mode_icons.get(mode, '🤖')
    mode_name = mode_names.get(mode, mode.upper())
    
    # Header
    click.echo(f"\n{icon} {mode_name}: {ticket_id.upper()}")
    click.echo("━" * 50)
    
    # Step 1: Fetch ticket
    click.echo("🔍 Fetching ticket data...", nl=False)
    try:
        issue = get_issue(ticket_id)
        
        # Debug: Check if we got a valid response
        if not isinstance(issue, dict):
            click.echo(f" ✗\n❌ Invalid response format: {type(issue)}")
            click.echo(f"Response: {issue}")
            return
            
        if 'fields' not in issue:
            click.echo(f" ✗\n❌ Missing 'fields' in response")
            click.echo(f"Available keys: {list(issue.keys())}")
            if 'errorMessages' in issue:
                click.echo(f"Error messages: {issue['errorMessages']}")
            return
            
        summary = issue['fields'].get('summary', 'No summary')
        click.echo(" ✓")
    except Exception as e:
        click.echo(f" ✗\n❌ Error fetching ticket: {e}")
        return
    
    # Extract description text
    description_obj = issue['fields'].get('description')
    if description_obj is None:
        description = "No description provided"
    else:
        description = extract_text_from_content(description_obj)
    
    # Step 2: AI Analysis (skip for RCA mode)
    if mode != 'rca':
        click.echo("🤖 Analyzing with Claude AI...", nl=False)
        try:
            prompt = generate_prompt(mode, summary, description)
            response = get_claude_response(prompt)
            click.echo(" ✓")
        except Exception as e:
            click.echo(f" ✗\n❌ Error with AI analysis: {e}")
            return
    
    # Step 3: Process response based on mode
    if mode == 'tag':
        handle_tag_mode(ticket_id, response)
    elif mode == 'rca':
        handle_rca_mode(ticket_id, issue, post_rca)
    else:
        handle_other_modes(ticket_id, mode, response)
    
    click.echo("━" * 50)
    click.echo(f"✅ {mode_name} complete!\n")

def generate_prompt(mode, summary, description):
    prompts = {
        "summarize": f"""Analyze this Jira ticket and provide:
1. Brief summary (2-3 sentences)
2. Key technical challenges
3. Estimated complexity (Simple/Medium/Complex)
4. Any risks or dependencies

Title: {summary}

Description: {description}""",
        "tag": f"""Suggest appropriate Jira tags/labels for this issue. Return ONLY a comma-separated list of tags (no explanations, bullet points, or extra text).

Issue: {summary}
Description: {description}

Tags:""",
        "subtasks": f"Break down this issue into smaller development subtasks:\n\n{summary}\n\n{description}",
        "test-notes": f"Generate QA test notes and edge cases:\n\n{summary}\n\n{description}",
        "rca": "RCA mode uses specialized prompt generation"
    }
    return prompts.get(mode, "")

def parse_tags_from_response(response):
    """Parse comma-separated tags from Claude response"""
    # Clean up the response and split into tags
    tags_text = response.strip()
    
    # Remove common prefixes/suffixes
    if tags_text.lower().startswith('tags:'):
        tags_text = tags_text[5:].strip()
    
    # Split by comma and clean each tag
    tags = [tag.strip().lower().replace(' ', '-') for tag in tags_text.split(',')]
    
    # Filter out empty tags and common stop words
    tags = [tag for tag in tags if tag and len(tag) > 1 and tag not in ['and', 'or', 'the', 'a', 'an']]
    
    return tags

def handle_tag_mode(ticket_id, response):
    """Handle tag mode with enhanced output"""
    click.echo("🏷️  Parsing and applying tags...", nl=False)
    try:
        suggested_tags = parse_tags_from_response(response)
        click.echo(" ✓")
        
        click.echo(f"📌 Applying {len(suggested_tags)} tags:")
        for tag in suggested_tags:
            click.echo(f"   • {tag}", nl=False)
            add_label(ticket_id, tag)
            click.echo(" ✓")
        
        click.echo("🔖 Adding audit label...", nl=False)
        add_label(ticket_id, 'ai-tagged')
        click.echo(" ✓")
        
        click.echo(f"\n🎯 Applied tags: {', '.join(suggested_tags)}")
        
    except Exception as e:
        click.echo(f" ✗\n❌ Error applying tags: {e}")

def handle_rca_mode(ticket_id, issue, post_rca=None):
    """Handle RCA mode - generate and save RCA as markdown file"""
    click.echo("🔍 Generating Root Cause Analysis...", nl=False)
    try:
        rca_data = generate_rca(issue)
        click.echo(" ✓")
        
        # Format as markdown
        markdown_content = format_rca_as_markdown(rca_data, issue)
        
        # Save to file
        click.echo("📝 Saving RCA to file...", nl=False)
        filepath = save_rca_to_file(ticket_id, markdown_content)
        click.echo(" ✓")
        
        click.echo(f"\n📄 RCA saved to: {filepath}")
        
        # Handle posting to Jira
        should_post = False
        if post_rca is not None:
            # Use command line option if provided
            should_post = post_rca
        else:
            # Try interactive prompt
            try:
                should_post = click.confirm("\n💬 Would you like to post this RCA to Jira as a comment?", default=False)
            except:
                # If interactive prompt fails, default to not posting
                click.echo("\n💡 Tip: Use --post-rca or --no-post-rca to avoid interactive prompt")
                should_post = False
        
        if should_post:
            click.echo("💬 Posting to Jira...", nl=False)
            formatted_rca = format_rca_for_jira(rca_data)
            post_comment(ticket_id, formatted_rca)
            click.echo(" ✓")
            
            click.echo("🔖 Adding 'rca-completed' label...", nl=False)
            add_label(ticket_id, 'rca-completed')
            click.echo(" ✓")
        else:
            click.echo("📋 RCA saved locally only.")
            
    except Exception as e:
        click.echo(f" ✗\n❌ Error generating RCA: {e}")

def handle_other_modes(ticket_id, mode, response):
    """Handle summarize, subtasks, and test-notes modes with enhanced output"""
    # Show a preview of the analysis
    preview = response[:150] + "..." if len(response) > 150 else response
    click.echo(f"\n📄 PREVIEW:")
    click.echo(f"   {preview}")
    
    click.echo(f"\n💬 Posting to Jira...", nl=False)
    try:
        post_comment(ticket_id, response)
        click.echo(" ✓")
    except Exception as e:
        click.echo(f" ✗\n❌ Error posting comment: {e}")
        return
    
    # Add label for summarize mode
    if mode == 'summarize':
        click.echo("🔖 Adding 'ai-reviewed' label...", nl=False)
        try:
            add_label(ticket_id, 'ai-reviewed')
            click.echo(" ✓")
        except Exception as e:
            click.echo(f" ✗\n❌ Error adding label: {e}")

if __name__ == '__main__':
    run()