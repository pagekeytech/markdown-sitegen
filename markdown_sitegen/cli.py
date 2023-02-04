import os
import shutil
import sys

import frontmatter
import jinja2
import markdown

from markdown_sitegen.lib import get_root_path


BUILD_DIR = 'build'
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'web')
STATIC_DIR = os.path.join(TEMPLATE_DIR, 'static')

def print_usage():
    print("Usage:")
    print("  markdown-sitegen <DIRECTORY>: generate website from markdown in directory")


def cli_entry_point():
    if len(sys.argv) == 2:
        gen_dir = sys.argv[1]
        if os.path.exists(gen_dir) and os.path.isdir(gen_dir):
            # Compute files to render, taking into account .sitegenignore
            files_to_render = []
            sitegenignore = []
            if os.path.exists(os.path.join(gen_dir, '.sitegenignore')):
                with open(os.path.join(gen_dir, '.sitegenignore')) as f:
                    sitegenignore = f.read().split('\n')
            for root, dirs, files in os.walk(gen_dir):
                if os.path.basename(root) in sitegenignore:
                    continue
                for filename in files:
                    if filename.lower().endswith('.md'):
                        files_to_render.append(os.path.join(root, filename))
            # Delete previous build dir
            shutil.rmtree(BUILD_DIR)
            # Render markdown to html
            env = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATE_DIR))
            post_template = env.get_template('post.html')
            for filename in files_to_render:
                with open(filename) as f:
                    post = frontmatter.load(f)
                    # Only publish the post if path specified
                    if 'path' in post:
                        html = markdown.markdown(post.content)
                        # Compute relative path to HTML file
                        relpath = post['path'] + '.html'
                        # Remove leading slash from path to HTML file
                        if relpath.startswith('/'):
                            relpath = relpath[1:]
                        out_filename = os.path.join(BUILD_DIR, relpath)
                        os.makedirs(os.path.dirname(out_filename), exist_ok=True)
                        # Render template
                        content = post_template.render(
                            body=html,
                            root_path=get_root_path(relpath),
                            blog_title="TODO support blog title",
                        )
                        with open(out_filename, 'w') as f:
                            f.write(content)
            # Render other pages like home, etc.
            index_template = env.get_template('index.html')
            content = index_template.render(
                blog_title="TODO support blog title"
            )
            with open(os.path.join(BUILD_DIR, 'index.html'), 'w') as f:
                f.write(content)
            # Copy static files into place
            shutil.copytree(STATIC_DIR, os.path.join(BUILD_DIR, 'static'))
        else:
            print("Error: not a directory - %s" % gen_dir)
    else:
        print_usage()
