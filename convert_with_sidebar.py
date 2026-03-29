import markdown
import sys

def convert_markdown_to_html(input_file, output_file, title, topbar_links):
    with open(input_file, 'r', encoding='utf-8') as f:
        markdown_content = f.read()

    md = markdown.Markdown(extensions=['fenced_code', 'tables', 'toc'])
    html_content = md.convert(markdown_content)
    
    left_sidebar_html = '<h3>On this page</h3>'
    if md.toc_tokens:
        for token in md.toc_tokens:
            left_sidebar_html += f'<a href="#{token["id"]}">{token["name"]}</a>'

    topbar_html = ''
    for link_title, link_href in topbar_links.items():
        topbar_html += f'<a href="{link_href}">{link_title}</a>'

    with open('template_with_sidebar.html', 'r', encoding='utf-8') as f:
        template_content = f.read()

    final_html = template_content.replace('{{title}}', title)
    final_html = final_html.replace('{{topbar}}', topbar_html)
    final_html = final_html.replace('{{left_sidebar}}', left_sidebar_html)
    final_html = final_html.replace('{{content}}', html_content)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(final_html)

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Usage: python convert_with_sidebar.py <input_markdown_file> <output_html_file> <title> [link_title:link_href]...")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]
    title = sys.argv[3]
    
    topbar_links = {}
    for arg in sys.argv[4:]:
        link_title, link_href = arg.split(':', 1)
        topbar_links[link_title] = link_href

    convert_markdown_to_html(input_file, output_file, title, topbar_links)
