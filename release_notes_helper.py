"""
Release Notes Helper for CJ-Buddy
Generates and manages release notes for Jira issues
"""

import click
from jira_helper import get_issue, update_field
from claude_helper import get_claude_response

def analyze_issue_for_release_notes(issue):
    """Analyze a Jira issue to extract relevant information for release notes"""
    fields = issue.get('fields', {})
    
    # Extract key information
    issue_type = fields.get('issuetype', {}).get('name', 'Unknown')
    summary = fields.get('summary', 'No summary')
    priority = fields.get('priority', {}).get('name', 'Unknown') if fields.get('priority') else 'Unknown'
    status = fields.get('status', {}).get('name', 'Unknown')
    assignee = fields.get('assignee', {}).get('displayName', 'Unassigned') if fields.get('assignee') else 'Unassigned'
    components = [comp.get('name') for comp in fields.get('components', [])]
    labels = fields.get('labels', [])
    
    # Extract description text (handle ADF format)
    from main import extract_text_from_content
    description_obj = fields.get('description')
    description = extract_text_from_content(description_obj) if description_obj else "No description"
    
    # Get any existing release notes
    existing_notes = fields.get('customfield_10424')  # Instructions/Operational Notes field
    
    return {
        'issue_type': issue_type,
        'summary': summary,
        'description': description,
        'priority': priority,
        'status': status,
        'assignee': assignee,
        'components': components,
        'labels': labels,
        'existing_notes': existing_notes
    }

def generate_release_notes_prompt(issue_data):
    """Generate a prompt for Claude to create release notes"""
    
    prompt = f"""You are a technical writer creating release notes for a software product. Analyze the following Jira issue and generate appropriate release note content.

ISSUE DETAILS:
- Type: {issue_data['issue_type']}
- Summary: {issue_data['summary']}
- Priority: {issue_data['priority']}
- Status: {issue_data['status']}
- Components: {', '.join(issue_data['components']) if issue_data['components'] else 'None'}
- Labels: {', '.join(issue_data['labels']) if issue_data['labels'] else 'None'}

DESCRIPTION:
{issue_data['description']}

EXISTING RELEASE NOTES:
{issue_data['existing_notes'] or 'None'}

Please generate release notes that:
1. Are written from the user's perspective (what they will experience)
2. Focus on the business value and impact
3. Are concise but informative
4. Use clear, non-technical language when possible
5. Follow this format if it's a new feature, bug fix, or improvement

For NEW FEATURES, use format:
"✨ **New**: [User-facing description of what's new]"

For BUG FIXES, use format:
"🐛 **Fixed**: [Description of what was broken and how it's fixed]"

For IMPROVEMENTS, use format:
"⚡ **Improved**: [Description of what's better/faster/easier]"

For BREAKING CHANGES, use format:
"⚠️ **Breaking**: [Description of what changed and impact]"

Respond with ONLY the release note text, no additional commentary."""

    return prompt

def ask_clarifying_questions(issue_data):
    """Ask user clarifying questions to improve release notes quality"""
    try:
        # Check if it's user-facing
        if not any(label in ['user-facing', 'customer-impact', 'ui', 'frontend'] for label in issue_data['labels']):
            click.echo("❓ Is this change visible to end users? (y/n): ", nl=False)
            is_user_facing = click.getchar().lower() == 'y'
            click.echo(is_user_facing)
            
            if not is_user_facing:
                click.echo("❓ Should this be included in release notes for internal teams? (y/n): ", nl=False)
                include_internal = click.getchar().lower() == 'y'
                click.echo(include_internal)
                if not include_internal:
                    return None, "Skipping - not user-facing and not for internal release notes"
        
        # Ask about business impact
        click.echo("\n❓ What's the main business value of this change?")
        click.echo("   (e.g., 'Improves performance', 'Reduces errors', 'New capability')")
        business_value = click.prompt("   Business value", default="").strip()
        
        # Ask about user impact
        click.echo("\n❓ How will users notice this change?")
        click.echo("   (e.g., 'Faster page loads', 'New button in dashboard', 'Error messages clearer')")
        user_impact = click.prompt("   User impact", default="").strip()
        
        # Ask about any caveats or limitations
        click.echo("\n❓ Any important limitations or caveats users should know?")
        caveats = click.prompt("   Limitations/caveats (optional)", default="").strip()
        
        additional_context = {
            'business_value': business_value,
            'user_impact': user_impact,
            'caveats': caveats
        }
        
        return additional_context, None
        
    except (OSError, click.exceptions.Abort):
        # Non-interactive environment, use defaults
        click.echo("⚠️ Non-interactive environment detected, using defaults")
        
        # Infer context from issue data
        issue_type = issue_data.get('issue_type', '').lower()
        labels = [label.lower() for label in issue_data.get('labels', [])]
        
        # Default context based on issue type and labels
        if 'bug' in issue_type:
            business_value = "Fixes functionality and improves user experience"
            user_impact = "Users will no longer experience the reported issue"
        elif any(word in issue_type for word in ['feature', 'story', 'epic']):
            business_value = "Adds new functionality to enhance product capabilities"
            user_impact = "Users gain access to new features and capabilities"
        else:
            business_value = "Improves system functionality and reliability"
            user_impact = "Users experience better system performance and stability"
        
        additional_context = {
            'business_value': business_value,
            'user_impact': user_impact,
            'caveats': ""
        }
        
        return additional_context, None

def enhance_prompt_with_context(base_prompt, additional_context):
    """Enhance the base prompt with additional context from user questions"""
    if not additional_context:
        return base_prompt
    
    enhancement = f"""

ADDITIONAL CONTEXT FROM USER:
- Business Value: {additional_context.get('business_value', 'N/A')}
- User Impact: {additional_context.get('user_impact', 'N/A')}
- Limitations/Caveats: {additional_context.get('caveats', 'N/A')}

Please incorporate this additional context into the release notes."""
    
    return base_prompt + enhancement

def review_and_edit_draft(draft_notes):
    """Allow user to review and edit the draft release notes"""
    click.echo("\n📝 DRAFT RELEASE NOTES:")
    click.echo("━" * 50)
    click.echo(draft_notes)
    click.echo("━" * 50)
    
    try:
        while True:
            click.echo("\n🔍 Review options:")
            click.echo("  1. ✅ Approve and save")
            click.echo("  2. ✏️  Edit manually")
            click.echo("  3. 🔄 Regenerate with different prompt")
            click.echo("  4. ❌ Cancel")
            
            choice = click.prompt("Choose an option", type=click.Choice(['1', '2', '3', '4']))
            
            if choice == '1':
                return draft_notes, True
            elif choice == '2':
                click.echo("\n✏️ Edit the release notes (press Enter twice when done):")
                lines = []
                while True:
                    line = input()
                    if line == "" and len(lines) > 0 and lines[-1] == "":
                        break
                    lines.append(line)
                # Remove the last empty line
                if lines and lines[-1] == "":
                    lines.pop()
                return '\n'.join(lines), True
            elif choice == '3':
                click.echo("\n🔄 Enter additional guidance for regeneration:")
                guidance = click.prompt("Additional guidance")
                return guidance, False  # Signal to regenerate
            elif choice == '4':
                return None, True  # Cancel
                
    except (OSError, click.exceptions.Abort):
        # Non-interactive environment, auto-approve
        click.echo("\n⚠️ Non-interactive environment detected, auto-approving draft")
        return draft_notes, True

def update_release_notes_field(ticket_id, new_content):
    """Update the Instructions/Operational Notes field with release notes"""
    # First get current content
    issue = get_issue(ticket_id)
    current_field = issue.get('fields', {}).get('customfield_10424')
    
    # Append new content with timestamp
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # Create the new content to append
    new_section = f"--- Release Notes ({timestamp}) ---\n{new_content}"
    
    # Handle both null and existing content
    if current_field is None:
        # Field is null, create new ADF content
        updated_content = {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": new_section
                        }
                    ]
                }
            ]
        }
    else:
        # Field has existing content, append to it
        if isinstance(current_field, str):
            # Convert plain text to ADF format
            full_content = f"{current_field}\n\n{new_section}"
        else:
            # Extract existing text from ADF and append
            from main import extract_text_from_content
            existing_text = extract_text_from_content(current_field)
            full_content = f"{existing_text}\n\n{new_section}"
        
        updated_content = {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": full_content
                        }
                    ]
                }
            ]
        }
    
    # Update the field
    update_field(ticket_id, 'customfield_10424', updated_content)
    return new_section

def generate_release_notes_for_issue(ticket_id):
    """Main function to generate and save release notes for an issue"""
    
    # Step 1: Fetch and analyze issue
    click.echo("🔍 Analyzing issue for release notes...", nl=False)
    try:
        issue = get_issue(ticket_id)
        issue_data = analyze_issue_for_release_notes(issue)
        click.echo(" ✓")
    except Exception as e:
        click.echo(f" ✗\n❌ Error analyzing issue: {e}")
        return
    
    # Step 2: Ask clarifying questions
    click.echo("❓ Gathering additional context...")
    additional_context, skip_reason = ask_clarifying_questions(issue_data)
    
    if skip_reason:
        click.echo(f"⏭️ {skip_reason}")
        return
    
    # Step 3: Generate initial draft
    attempts = 0
    max_attempts = 3
    
    while attempts < max_attempts:
        click.echo(f"🤖 Generating release notes (attempt {attempts + 1})...", nl=False)
        try:
            base_prompt = generate_release_notes_prompt(issue_data)
            enhanced_prompt = enhance_prompt_with_context(base_prompt, additional_context)
            
            draft_notes = get_claude_response(enhanced_prompt)
            click.echo(" ✓")
            break
        except Exception as e:
            attempts += 1
            click.echo(f" ✗\n❌ Error generating release notes: {e}")
            if attempts >= max_attempts:
                return
            click.echo("🔄 Retrying...")
    
    # Step 4: Review and edit loop
    while True:
        result, is_final = review_and_edit_draft(draft_notes)
        
        if result is None:  # User cancelled
            click.echo("❌ Release notes generation cancelled")
            return
        
        if is_final:  # User approved
            final_notes = result
            break
        else:  # User wants to regenerate
            # Regenerate with additional guidance
            regeneration_prompt = f"{enhanced_prompt}\n\nADDITIONAL GUIDANCE: {result}"
            click.echo("🤖 Regenerating with your guidance...", nl=False)
            try:
                draft_notes = get_claude_response(regeneration_prompt)
                click.echo(" ✓")
            except Exception as e:
                click.echo(f" ✗\n❌ Error regenerating: {e}")
                return
    
    # Step 5: Save to Jira
    click.echo("💾 Saving release notes to Jira...", nl=False)
    try:
        updated_content = update_release_notes_field(ticket_id, final_notes)
        click.echo(" ✓")
        
        click.echo(f"\n✅ Release notes saved successfully!")
        click.echo(f"📝 Content appended to Instructions/Operational Notes field")
        
    except Exception as e:
        click.echo(f" ✗\n❌ Error saving to Jira: {e}")
        click.echo(f"\n📋 Generated content (save manually if needed):")
        click.echo("━" * 50)
        click.echo(final_notes)
        click.echo("━" * 50)