import os
import markdown
import re

def get_project_name_from_markdown(markdown_content):
    """Extracts the first H1 header from markdown content to use as a title."""
    match = re.search(r'^#\s+(.*)', markdown_content, re.MULTILINE)
    if match:
        return match.group(1).strip()
    return "Untitled Project"

def parse_index_markdown(markdown_content):
    """Parses the INDEX.md file to extract hero content and project descriptions."""
    hero_html = ""
    descriptions = {}

    # Split content by the horizontal rule '---'
    parts = re.split(r'\n---\n', markdown_content, maxsplit=1)

    # Part 1: Hero content
    if len(parts) > 0:
        hero_md = parts[0]
        hero_title_match = re.search(r'^#\s+(.*)', hero_md, re.MULTILINE)
        # Find the first paragraph that is not the title
        hero_subtitle_match = re.search(r'^\s*([^#\n].*)', hero_md, re.MULTILINE)

        title_text = hero_title_match.group(1).strip() if hero_title_match else ""
        # Make '3Deer' green
        title_text = title_text.replace("3Deer", "<span>3Deer</span>")

        subtitle_text = hero_subtitle_match.group(1).strip() if hero_subtitle_match else ""

        hero_html = f"<h1>{title_text}</h1>\n<p>{subtitle_text}</p>"

    # Part 2: Project descriptions
    if len(parts) > 1:
        desc_md = parts[1]
        # Find all H2 headers and the content that follows them
        project_sections = re.split(r'\n##\s+', desc_md)[1:] # Split and remove first empty element
        for section in project_sections:
            lines = section.strip().split('\n', 1)
            project_dir = lines[0].strip()
            description = lines[1].strip() if len(lines) > 1 else ""
            descriptions[project_dir] = description

    return hero_html, descriptions

GITHUB_REPOS = {
    "android-model-engine": "https://github.com/the3deer/android-3D-engine",
    "android-model-viewer": "https://github.com/the3deer/android-3D-model-viewer",
    "android-game-isomodel": "https://github.com/the3deer/android-3D-isogame"
}

def generate_site(root_dir="."):
    """
    Generates the static HTML site from markdown files.
    """
    print("Starting site generation...")

    # --- 1. Find all project directories ---
    # A project is a directory with a README.md inside.
    projects = []
    for item in os.listdir(root_dir):
        item_path = os.path.join(root_dir, item)
        # Ensure it's a directory, contains a README, and isn't a hidden/special folder.
        if (os.path.isdir(item_path) and
                os.path.exists(os.path.join(item_path, 'README.md')) and
                not item.startswith('.') and not item.startswith('_')):
            projects.append(item)

    if not projects:
        print("No project directories found. A project needs a folder with a README.md file.")
        return

    print(f"Found projects: {', '.join(projects)}")

    # --- 2. Read the project page HTML template ---
    project_template_path = os.path.join(root_dir, 'project_template.html')
    try:
        with open(project_template_path, 'r', encoding='utf-8') as f:
            project_template_html = f.read()
    except FileNotFoundError:
        print(f"Error: Template file not found at '{project_template_path}'")
        return

    # --- 3. Generate the top menu HTML (shared across all pages) ---
    top_menu_items = []
    for project_dir in sorted(projects):
        project_name_display = project_dir.replace('-', ' ').title()
        html_file = f"{project_dir}.html"
        top_menu_items.append(f'<a href="{html_file}">{project_name_display}</a>')
    top_menu_html = "\n            ".join(top_menu_items)

    # --- 4. Process each project to generate its HTML page ---
    for project_dir in projects:
        print(f"Processing '{project_dir}'...")

        # a. Read the project's README.md
        readme_path = os.path.join(root_dir, project_dir, 'README.md')
        with open(readme_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()

        # b. Get project name from the first H1 tag
        project_name = get_project_name_from_markdown(markdown_content)
        if project_name == "Untitled Project":
            project_name = project_dir.replace('-', ' ').title()  # Fallback to folder name

        # c. Convert markdown to HTML and generate the sidebar table of contents
        md_extensions = [
            'toc',          # Generates a table of contents
            'fenced_code',  # Supports GitHub-style code blocks (```)
            'tables',       # Supports Markdown tables
            'attr_list'     # Allows adding HTML attributes to elements
        ]
        md = markdown.Markdown(extensions=md_extensions)

        main_content_html = md.convert(markdown_content)

        # d. Fix relative image/link paths. Markdown paths are relative to the README.md
        #    (e.g., ./screenshots/img.png), but the final HTML is in the root.
        #    We prepend the project directory to fix them.
        main_content_html = re.sub(r'(src|href)=(["\'])\./', fr'\1=\2{project_dir}/', main_content_html)

        sidebar_menu_html = f'<h3>On this page</h3>\n{md.toc}' if md.toc else ''

        # e. Get the project's specific GitHub URL
        github_url = GITHUB_REPOS.get(project_dir, "https://github.com/the3deer/the3deer.github.io") # Fallback

        # f. Populate the template with the generated content
        final_html = project_template_html
        final_html = final_html.replace('{{project_name}}', project_name)
        final_html = final_html.replace('{{top_menu}}', top_menu_html)
        final_html = final_html.replace('{{github_url}}', github_url)
        final_html = final_html.replace('{{sidebar_menu}}', sidebar_menu_html)
        final_html = final_html.replace('{{main_content}}', main_content_html)

        # g. Write the final HTML file to the root directory
        output_path = os.path.join(root_dir, f"{project_dir}.html")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(final_html)

        print(f"  - Successfully generated '{output_path}'")

    # --- 5. Generate the root index.html page ---
    print("\nGenerating root index.html...")
    index_md_path = os.path.join(root_dir, 'INDEX.md')
    index_template_path = os.path.join(root_dir, 'index_template.html')

    if not os.path.exists(index_md_path) or not os.path.exists(index_template_path):
        print("  - Skipping: INDEX.md or index_template.html not found.")
    else:
        # a. Read templates and source markdown
        with open(index_template_path, 'r', encoding='utf-8') as f:
            index_template_html = f.read()
        with open(index_md_path, 'r', encoding='utf-8') as f:
            index_markdown_content = f.read()

        # b. Parse INDEX.md for hero content and descriptions
        hero_content_html, project_descriptions = parse_index_markdown(index_markdown_content)

        # c. Generate project cards HTML
        project_cards_list = []
        for project_dir in sorted(projects):
            # Get project title from its own README
            readme_path = os.path.join(root_dir, project_dir, 'README.md')
            with open(readme_path, 'r', encoding='utf-8') as f:
                project_readme_content = f.read()

            project_title = get_project_name_from_markdown(project_readme_content)
            if project_title == "Untitled Project":
                project_title = project_dir.replace('-', ' ').title()

            # Get description from the parsed INDEX.md
            project_desc = project_descriptions.get(project_dir, "No description available.")
            html_file = f"{project_dir}.html"

            # Assemble card HTML
            card_html = f'<a href="{html_file}" class="card">\n    <h2>{project_title}</h2>\n    <p>{project_desc}</p>\n    <div class="card-link">View Documentation →</div>\n</a>'
            project_cards_list.append(card_html)

        project_cards_html = "\n".join(project_cards_list)

        # d. Populate the index template
        final_index_html = index_template_html
        final_index_html = final_index_html.replace('{{top_menu}}', top_menu_html)
        final_index_html = final_index_html.replace('{{hero_content}}', hero_content_html)
        final_index_html = final_index_html.replace('{{project_cards}}', project_cards_html)

        # e. Write the final index.html
        output_path = os.path.join(root_dir, "index.html")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(final_index_html)

        print(f"  - Successfully generated '{output_path}'")

    print("\nSite generation complete!")

if __name__ == '__main__':
    generate_site()