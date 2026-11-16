"""Draws the profile's editor panels: Hierarchy, Console, Inspector and Timeline, as one SVG.

Runs daily in this repo's workflow, on the public data GitHub's API gives the workflow's own token, so nothing private
is listed. Usage: editor.py <snake.svg> <out.svg>; GITHUB_TOKEN and LOGIN come from the environment.
Icons are glyphs of Lucide (ISC license), the icon font vkmEngine's editor uses.
"""
import json, os, re, sys, urllib.request
from xml.sax.saxutils import escape

W = 1000
GAP, PANEL, RAISED, FIELD, HAIR = "#16171A", "#1E1F23", "#26282D", "#141518", "#2A2C31"
TEXT, TEXT2, ACCENT, WARN = "#E6E7EA", "#8A8D96", "#4A9EFF", "#F0AD3E"
SANS = "Roboto, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif"
MONO = "ui-monospace, 'Cascadia Mono', Consolas, 'DejaVu Sans Mono', Menlo, monospace"
FAMILY = ["vkmOpenGL", "vkmVulkan", "vkmPhysics", "vkmNetwork", "vkmAudio", "vkmPlatform", "vkmLog"]
ICONS = {
    "globe": "M11.59 1.01Q8.42 1.18 5.88 2.88Q4.15 4.04 2.96 5.73Q1.78 7.42 1.3 9.44Q1.01 10.66 1.01 12Q1.01 13.06 1.18 14.01Q1.34 14.96 1.73 15.94Q2.54 18.07 4.2 19.74Q5.86 21.41 7.99 22.25Q9 22.64 9.95 22.82Q10.9 23 12 23Q13.3 23 14.46 22.73Q15.62 22.47 16.78 21.91Q18.94 20.86 20.48 19Q22.03 17.14 22.63 14.82Q23.23 12.51 22.84 10.16Q22.44 7.8 21.1 5.84Q19.7 3.79 17.58 2.53Q15.46 1.27 13.01 1.06Q12.17 0.99 11.59 1.01ZM9.62 3.39Q7.75 6.17 7.22 9.44Q7.15 9.72 7.1 10.19Q7.06 10.66 7.06 10.78V10.83Q7.06 10.95 7 10.97Q6.94 10.99 6.62 11.02H3.05L3.07 10.85Q3.22 9.75 3.66 8.64Q4.1 7.54 4.78 6.65Q6.5 4.32 9.31 3.41L9.65 3.32Q9.67 3.32 9.62 3.39ZM15.19 3.6Q16.97 4.25 18.36 5.64Q19.75 7.04 20.42 8.81Q20.81 9.84 20.93 10.85L20.95 11.02H17.38Q17.06 10.99 17 10.97Q16.94 10.95 16.94 10.83V10.78Q16.94 10.66 16.9 10.19Q16.85 9.72 16.78 9.41Q16.25 6.17 14.4 3.39L14.33 3.32L14.59 3.39Q14.83 3.46 15.19 3.6ZM12.24 3.84Q13.34 5.26 14.04 7.02Q14.74 8.79 14.9 10.49L14.95 11.02H9.02L9.1 10.52Q9.24 8.96 9.82 7.37Q10.39 5.79 11.33 4.44Q11.52 4.16 11.75 3.84Q11.98 3.53 12 3.54Q12.02 3.55 12.24 3.84ZM7.03 13.04Q7.06 13.08 7.06 13.21Q7.06 13.35 7.1 13.81Q7.15 14.28 7.22 14.57Q7.75 17.84 9.6 20.62L9.67 20.69L9.41 20.62Q6.55 19.75 4.78 17.36Q4.1 16.47 3.66 15.36Q3.22 14.26 3.07 13.15L3.05 12.99L6.7 13.01Q7.01 13.01 7.03 13.04ZM14.95 13.08Q14.93 13.18 14.9 13.49Q14.78 14.79 14.34 16.16Q13.9 17.52 13.22 18.7Q12.96 19.16 12.5 19.8Q12.05 20.45 12 20.45Q11.95 20.45 11.5 19.8Q11.04 19.16 10.78 18.7Q10.1 17.52 9.66 16.16Q9.22 14.79 9.1 13.49L9.02 12.99H14.95ZM20.93 13.15Q20.64 15.44 19.24 17.34Q17.83 19.25 15.72 20.21Q15.31 20.38 14.82 20.55Q14.33 20.71 14.35 20.67L14.47 20.5Q15.19 19.39 15.78 18Q16.37 16.61 16.66 15.22Q16.78 14.74 16.86 14.1Q16.94 13.47 16.94 13.23V13.18Q16.94 13.06 17 13.04Q17.06 13.01 17.38 12.99H20.95Z",
    "box": "M11.4 1.04Q11.02 1.14 10.66 1.31Q10.42 1.43 6.95 3.42Q3.48 5.41 3.34 5.51Q2.33 6.18 2.06 7.36Q2.02 7.55 2.02 8.2V11.99V15.66Q2.02 16.4 2.06 16.57Q2.18 17.17 2.52 17.66Q2.86 18.16 3.36 18.49Q3.67 18.68 7.14 20.66Q10.61 22.64 10.78 22.72Q11.11 22.86 11.38 22.92Q11.64 22.98 12.01 22.98Q12.38 22.98 12.68 22.91Q12.98 22.84 13.34 22.64Q13.61 22.52 16.99 20.59Q20.38 18.66 20.62 18.49Q21.14 18.16 21.48 17.66Q21.82 17.17 21.94 16.57Q21.98 16.4 21.98 15.66V11.99V8.32Q21.98 7.57 21.94 7.4Q21.82 6.85 21.49 6.35Q21.17 5.84 20.71 5.53Q20.5 5.39 17.02 3.4Q13.54 1.4 13.27 1.28Q12.96 1.14 12.72 1.08Q12.48 1.02 12.07 1.02Q11.59 1.02 11.4 1.04ZM12.38 3.08Q12.55 3.16 15.76 4.99Q18.96 6.83 18.96 6.84Q18.96 6.85 15.5 8.83Q12.05 10.81 12 10.81Q11.95 10.81 8.5 8.83Q5.04 6.85 5.04 6.84Q5.04 6.83 8.23 5Q11.42 3.18 11.56 3.11Q11.69 3.04 11.78 3.01Q11.88 2.99 12.08 3.01Q12.29 3.04 12.38 3.08ZM7.54 10.57 11.02 12.56V16.57Q11.02 20.58 10.99 20.56L7.7 18.68Q4.42 16.81 4.31 16.7Q4.2 16.6 4.1 16.4L4.01 16.21V9.25Q4.01 8.53 4.03 8.56ZM19.99 12.88V16.21L19.9 16.4Q19.8 16.6 19.69 16.7Q19.58 16.81 16.3 18.68L13.01 20.56Q12.98 20.58 12.98 16.57V12.56L19.99 8.56V9.04Q20.02 9.54 19.99 12.88Z",
    "down": "M5.74 8.04Q5.3 8.18 5.09 8.57Q5.02 8.71 5.02 9Q5.02 9.29 5.1 9.44Q5.18 9.6 8.29 12.71Q11.4 15.82 11.56 15.9Q11.71 15.98 12 15.98Q12.29 15.98 12.44 15.9Q12.6 15.82 15.71 12.71Q18.82 9.6 18.9 9.44Q18.98 9.29 18.98 9Q18.98 8.71 18.91 8.57Q18.74 8.28 18.43 8.11Q18.34 8.06 18.26 8.04Q18.19 8.02 18 8.02Q17.81 8.02 17.74 8.04Q17.66 8.06 17.54 8.11Q17.38 8.21 14.69 10.9L12 13.58L7.15 8.76Q6.62 8.26 6.43 8.11Q6.29 8.02 6.1 8.02H6.05Q5.81 8.02 5.74 8.04Z",
    "right": "M8.74 5.04Q8.3 5.18 8.09 5.57Q8.02 5.71 8.02 6Q8.02 6.29 8.09 6.43Q8.16 6.58 10.87 9.29L13.58 12L10.87 14.71Q8.16 17.42 8.09 17.57Q8.02 17.71 8.02 17.98Q8.02 18.24 8.08 18.38Q8.14 18.53 8.3 18.7Q8.47 18.86 8.62 18.92Q8.76 18.98 9.02 18.98Q9.29 18.98 9.44 18.9Q9.6 18.82 12.71 15.71Q15.82 12.6 15.9 12.44Q15.98 12.29 15.98 12Q15.98 11.71 15.91 11.57Q15.84 11.42 12.72 8.3L10.25 5.86Q9.67 5.28 9.46 5.14Q9.29 5.02 9.12 5.02H9.05Q8.81 5.02 8.74 5.04Z",
    "terminal": "M3.82 4.01Q3.49 4.06 3.27 4.31Q3.05 4.57 3.02 4.91Q2.98 5.26 3.17 5.55Q3.27 5.67 5.93 8.31L8.6 10.97L5.89 13.69Q4.06 15.51 3.62 15.98Q3.17 16.45 3.1 16.57Q2.91 16.97 3.08 17.36Q3.25 17.74 3.63 17.91Q4.01 18.08 4.42 17.89Q4.54 17.81 5.07 17.31Q5.6 16.81 7.71 14.69Q10.83 11.57 10.9 11.45Q11 11.26 11 11.01Q11 10.76 10.9 10.54Q10.85 10.45 7.71 7.3Q5.62 5.19 5.07 4.66Q4.52 4.13 4.42 4.09Q4.13 3.97 3.82 4.01ZM11.77 18.01Q11.55 18.05 11.36 18.23Q11.17 18.41 11.07 18.63Q10.95 18.99 11.09 19.36Q11.24 19.73 11.6 19.9L11.79 19.97L18.89 20Q19.81 19.97 20.12 19.95Q20.33 19.95 20.47 19.88Q20.6 19.81 20.72 19.67Q20.84 19.54 20.91 19.4Q21.08 19.01 20.93 18.63Q20.79 18.25 20.38 18.05L20.24 18.01L16.06 17.98Q11.91 17.98 11.77 18.01Z",
    "film": "M4.46 2.06Q3.6 2.21 2.96 2.81Q2.33 3.41 2.09 4.3Q2.04 4.44 2.04 5.52L2.02 12L2.04 18.48Q2.04 19.56 2.09 19.7Q2.33 20.54 2.89 21.11Q3.46 21.67 4.3 21.91Q4.44 21.96 5.52 21.96L12 21.98L18.48 21.96Q19.56 21.96 19.7 21.91Q20.54 21.67 21.11 21.11Q21.67 20.54 21.91 19.7Q21.96 19.56 21.96 18.48L21.98 12L21.96 5.52Q21.96 4.44 21.91 4.3Q21.7 3.46 21.13 2.89Q20.57 2.33 19.75 2.09L19.51 2.02H12.1Q4.66 2.02 4.46 2.06ZM6 5.26V6.5H3.98L4.01 4.78L4.08 4.61Q4.2 4.37 4.4 4.21Q4.61 4.06 4.85 4.01Q4.99 4.01 5.5 3.98H6ZM15.98 7.49V11.02H8.02V3.98H15.98ZM19.39 4.08Q19.75 4.25 19.92 4.61L19.99 4.78L20.02 6.5H18V3.98H18.6Q19.06 4.01 19.16 4.02Q19.27 4.03 19.39 4.1ZM6 9.74V11.02H3.98V8.5H6ZM20.02 9.74V11.02H18V8.5H20.02ZM6 14.26V15.5H3.98V12.98H6ZM15.98 16.49V20.02H8.02V12.98H15.98ZM20.02 14.26V15.5H18V12.98H20.02ZM6 18.74V20.02H5.5Q5.09 20.02 4.88 19.99Q4.68 19.97 4.54 19.9Q4.25 19.73 4.08 19.39L4.01 19.22L3.98 17.5H6ZM20.02 18.36 19.99 19.22 19.92 19.39Q19.75 19.73 19.46 19.9Q19.32 19.97 19.12 19.99Q18.91 20.02 18.5 20.02H18V17.5H20.02Z",
    "folder": "M3.39 2.56Q2.57 2.72 1.96 3.31Q1.35 3.9 1.11 4.69Q1.04 4.93 1.04 5.29Q1.01 5.75 0.99 7.24L1.01 17.92Q1.04 18.97 1.06 19.12Q1.3 20.05 1.95 20.66Q2.6 21.28 3.51 21.44Q3.8 21.49 12.01 21.49Q20.21 21.49 20.5 21.44Q21.41 21.28 22.07 20.66Q22.73 20.05 22.95 19.12Q22.97 18.97 23 18.13V13.69Q23.02 8.48 23 8.2Q22.88 7.33 22.4 6.68Q21.77 5.87 20.74 5.58L20.5 5.51L11.86 5.48L11.69 5.41Q11.5 5.32 11.41 5.22Q11.31 5.12 10.83 4.4Q10.45 3.85 10.23 3.59Q10.01 3.32 9.8 3.16Q9.61 3.01 9.34 2.86Q9.08 2.7 8.89 2.65Q8.53 2.53 8.15 2.52Q7.78 2.51 5.96 2.51H3.97Q3.56 2.53 3.39 2.56ZM8.33 4.57Q8.53 4.67 8.63 4.79Q8.74 4.91 9.21 5.6Q9.68 6.3 9.97 6.59Q10.54 7.16 11.33 7.4L11.57 7.48H15.89Q20.21 7.5 20.31 7.54Q20.41 7.57 20.55 7.67Q20.69 7.76 20.77 7.84Q20.84 7.91 20.91 8.08L20.98 8.24V18.76L20.91 18.92Q20.72 19.28 20.36 19.43L20.19 19.48H3.82L3.65 19.43Q3.29 19.28 3.1 18.92L3.03 18.76V5.24L3.1 5.08Q3.2 4.86 3.39 4.7Q3.58 4.55 3.82 4.52Q3.99 4.5 6.05 4.5H8.14Z",
    "star": "M11.79 1.49Q11.31 1.54 10.93 1.93Q10.78 2.07 10.7 2.21Q10.62 2.36 10.33 2.96Q8.84 5.96 8.52 6.58Q8.19 7.21 8.05 7.34Q7.9 7.47 7.75 7.53Q7.59 7.59 4.98 7.97Q2.36 8.36 2.17 8.41Q1.78 8.5 1.47 8.81Q1.28 9.01 1.18 9.17Q1.09 9.34 1.03 9.61Q0.97 9.87 1.04 10.17Q1.11 10.47 1.28 10.73Q1.35 10.88 3.34 12.8L3.54 12.97Q4.62 14.05 4.93 14.33Q5.34 14.77 5.43 14.93Q5.5 15.08 5.53 15.29V15.32Q5.53 15.49 5.46 15.99Q5.38 16.49 5.07 18.2Q4.64 20.86 4.64 21.01Q4.64 21.61 5.1 22.09Q5.43 22.4 5.86 22.49Q6.18 22.57 6.49 22.49Q6.66 22.45 6.97 22.3L9.82 20.81Q11.22 20.07 11.48 19.95Q11.74 19.83 11.89 19.83L11.96 19.81Q12.2 19.81 12.39 19.88Q12.58 19.95 14.74 21.1L17.05 22.3Q17.36 22.45 17.53 22.49Q17.84 22.57 18.15 22.49Q18.61 22.4 18.92 22.09Q19.38 21.61 19.38 21.01Q19.38 20.84 18.94 18.22Q18.63 16.52 18.56 16.01Q18.49 15.51 18.49 15.34V15.29Q18.51 15.08 18.58 14.96Q18.68 14.77 19.09 14.36Q19.38 14.07 20.46 13.01L20.67 12.8Q22.64 10.88 22.76 10.71Q23 10.33 23 9.88Q23 9.44 22.76 9.05Q22.62 8.81 22.35 8.63Q22.09 8.45 21.8 8.38Q21.66 8.36 19.04 7.97Q16.42 7.59 16.27 7.53Q16.11 7.47 15.97 7.34Q15.82 7.21 15.51 6.61Q15.2 6.01 13.71 2.98Q13.4 2.38 13.32 2.23Q13.23 2.07 13.09 1.93Q12.7 1.54 12.27 1.49L12.06 1.47Q11.98 1.47 11.79 1.49ZM12.99 6.05Q13.98 8.02 14.1 8.21Q14.22 8.41 14.53 8.71Q14.84 9.01 15.03 9.15Q15.46 9.39 15.94 9.51Q16.18 9.58 18.27 9.88Q20.36 10.18 20.41 10.21Q20.43 10.21 20.36 10.28L19.86 10.81L18.42 12.2Q17.22 13.37 17.1 13.54Q16.74 14.05 16.54 14.72Q16.5 14.91 16.5 15.41V15.89L16.86 18.01Q17.24 20.12 17.23 20.13Q17.22 20.14 15.87 19.42L15.78 19.37Q14.12 18.51 13.66 18.27Q13.02 17.96 12.7 17.89Q12.46 17.81 12.03 17.81H11.98Q11.55 17.81 11.31 17.89Q11 17.96 10.35 18.27Q9.9 18.51 8.24 19.37L8.14 19.42Q6.8 20.14 6.79 20.13Q6.78 20.12 7.16 18.01L7.52 15.89V15.39Q7.52 14.91 7.47 14.72Q7.28 14.05 6.92 13.54Q6.8 13.37 5.62 12.22L3.87 10.52Q3.58 10.23 3.61 10.21Q3.63 10.18 5.74 9.88Q7.86 9.58 8.07 9.51Q8.7 9.37 9.2 8.98Q9.7 8.6 10.04 8.05Q10.14 7.85 11.06 5.97Q11.98 4.09 12.01 4.09Q12.03 4.09 12.99 6.05Z",
    "info": "M11.47 1.03Q9.48 1.1 7.65 1.89Q5.83 2.68 4.39 4.06Q2.95 5.44 2.09 7.24Q1.25 8.97 1.05 10.94Q1.01 11.28 1.01 12Q1.01 12.72 1.05 13.05Q1.25 15.02 2.09 16.75Q3.21 19.15 5.34 20.76Q7.46 22.36 10.05 22.82Q10.97 22.99 12 22.99Q13.29 22.99 14.46 22.72Q15.62 22.46 16.77 21.91Q18.93 20.85 20.48 18.99Q22.03 17.13 22.63 14.8Q23.13 12.88 22.94 10.94Q22.75 9 21.91 7.22Q20.9 5.16 19.14 3.64Q17.37 2.13 15.17 1.46Q13.44 0.93 11.47 1.03ZM13.13 3.07Q14.97 3.31 16.55 4.23Q18.12 5.16 19.22 6.64Q20.64 8.54 20.95 11.01Q20.97 11.3 20.97 12Q20.97 12.69 20.95 12.98Q20.71 14.97 19.71 16.63Q18.72 18.28 17.09 19.41Q16.27 19.99 15.29 20.37Q14.3 20.76 13.25 20.9Q12.81 20.97 12 20.97Q11.18 20.97 10.75 20.9Q8.9 20.64 7.39 19.72Q5.88 18.81 4.77 17.35Q3.36 15.45 3.05 12.98Q3.02 12.69 3.02 12Q3.02 11.3 3.05 11.01Q3.29 9.09 4.2 7.5Q5.11 5.9 6.65 4.77Q7.58 4.08 8.72 3.62Q9.86 3.16 10.99 3.07L11.42 3.02Q11.59 3 12.24 3.02Q12.89 3.04 13.13 3.07ZM11.83 7.03Q11.52 7.08 11.28 7.32Q10.92 7.68 11.01 8.18Q11.11 8.68 11.57 8.9Q11.73 8.97 12 8.97Q12.43 8.97 12.72 8.68Q12.93 8.47 12.98 8.16Q13.08 7.65 12.72 7.29Q12.36 6.93 11.83 7.03ZM11.73 11.04Q11.3 11.18 11.09 11.56L11.01 11.71V15.93Q11.01 16.24 11.07 16.39Q11.13 16.53 11.28 16.68Q11.42 16.82 11.6 16.9Q11.78 16.99 12 16.99Q12.21 16.99 12.39 16.9Q12.57 16.82 12.72 16.68Q12.86 16.53 12.92 16.39Q12.98 16.24 12.98 15.93V11.71L12.91 11.56Q12.74 11.25 12.43 11.11Q12.29 11.04 12.05 11.02Q11.81 11.01 11.73 11.04Z"
}

QUERY = """query($login: String!) {
  user(login: $login) {
    login
    contributionsCollection {
      totalCommitContributions totalPullRequestContributions contributionCalendar { totalContributions }
    }
    repositories(first: 100, ownerAffiliations: OWNER, privacy: PUBLIC, isFork: false,
                 orderBy: {field: PUSHED_AT, direction: DESC}) {
      totalCount
      nodes {
        name stargazerCount pushedAt
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) { edges { size node { name color } } }
        defaultBranchRef { target { ... on Commit { history(first: 6) { nodes { messageHeadline committedDate } } } } }
      }
    }
  }
}"""


def fetch(login, token):
    req = urllib.request.Request("https://api.github.com/graphql",
                                 data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
                                 headers={"Authorization": "bearer " + token, "Content-Type": "application/json"})
    reply = json.load(urllib.request.urlopen(req, timeout=60))
    if reply.get("errors"):
        raise SystemExit("GitHub said: " + json.dumps(reply["errors"]))
    return reply["data"]["user"]


def icon(name, x, y, size, color):
    s = size / 24
    return f'<path transform="translate({x:.1f},{y:.1f}) scale({s:.4f})" fill="{color}" d="{ICONS[name]}"/>'


def text(x, y, s, size=12, color=TEXT, anchor="start", weight=400, family=SANS):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{family}" font-size="{size}" font-weight="{weight}" '
            f'fill="{color}" text-anchor="{anchor}" dominant-baseline="central">{escape(s)}</text>')


def clip(s, n):
    return s if len(s) <= n else s[:n - 1] + "…"


def tabs(x, y, w, names, active):
    """A panel's tab strip: the active tab raised, with the accent under it, as the editor draws it."""
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="26" fill="{PANEL}"/>',
           f'<rect x="{x}" y="{y + 25}" width="{w}" height="1" fill="{HAIR}"/>']
    tx = x
    for n in names:
        tw = 14 + 6.6 * len(n)
        if n == active:
            out.append(f'<rect x="{tx}" y="{y}" width="{tw:.1f}" height="26" fill="{RAISED}"/>')
            out.append(f'<rect x="{tx}" y="{y + 24}" width="{tw:.1f}" height="2" fill="{ACCENT}"/>')
        out.append(text(tx + 7, y + 13, n, 12, TEXT if n == active else TEXT2))
        tx += tw
    return out


def hierarchy(x, y, w, h, user, repos):
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{PANEL}"/>'] + tabs(x, y, w, ["Hierarchy"], "Hierarchy")
    byname = {r["name"]: r for r in repos}
    rows = [(0, "down", "globe", "World", None, True)]
    if "vkmEngine" in byname:
        rows.append((1, "down", "box", "vkmEngine", byname["vkmEngine"]["stargazerCount"], True))
        rows += [(2, None, "box", n, byname[n]["stargazerCount"], False) for n in FAMILY if n in byname]
    others = [r for r in repos if r["name"] not in FAMILY + ["vkmEngine", user["login"]]]
    room = int((h - 26 - 26) // 19) - len(rows)
    rows += [(1, None, "box", r["name"], r["stargazerCount"], False) for r in others[:max(room, 0)]]
    cy = y + 26 + 6
    for depth, chev, ic, name, stars, bold in rows:
        ix = x + 10 + depth * 14
        if chev:
            out.append(icon(chev, ix, cy + 3, 12, TEXT2))
        out.append(icon(ic, ix + 14, cy + 2, 14, TEXT if bold else TEXT2))
        out.append(text(ix + 34, cy + 9, clip(name, 22), 12, TEXT, weight=500 if bold else 400))
        if stars:
            out.append(icon("star", x + w - 30, cy + 3, 11, WARN))
            out.append(text(x + w - 10, cy + 9, str(stars), 11, TEXT2, "end"))
        cy += 19
    out.append(f'<rect x="{x}" y="{y + h - 22}" width="{w}" height="1" fill="{HAIR}"/>')
    out.append(text(x + 10, y + h - 11, f"{len(repos)} public repositories", 11, TEXT2))
    return out


def console(x, y, w, h, user, repos):
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{FIELD}"/>']
    out += tabs(x, y, w, ["Assets", "Animation", "Console"], "Console")
    lines = []
    for r in repos:
        if r["name"] == user["login"] or not r.get("defaultBranchRef"):
            continue
        for c in r["defaultBranchRef"]["target"]["history"]["nodes"]:
            if not c["messageHeadline"].startswith("Merge "):
                lines.append((c["committedDate"], r["name"], c["messageHeadline"]))
    lines.sort(reverse=True)
    n = int((h - 26 - 8) // 19)
    chars = int((w - 20) / 6.6)
    cy = y + 26 + 13
    for date, repo, msg in lines[:n]:
        stamp = f"[{date[5:10]} {date[11:16]}]"
        tag = f"[{repo}]"
        rest = clip(msg, max(chars - len(stamp) - len(tag) - 2, 8))
        out.append(f'<text x="{x + 10}" y="{cy:.1f}" font-family="{MONO}" font-size="11" dominant-baseline="central">'
                   f'<tspan fill="{TEXT2}">{escape(stamp)}</tspan> <tspan fill="{ACCENT}">{escape(tag)}</tspan> '
                   f'<tspan fill="{TEXT}">{escape(rest)}</tspan></text>')
        cy += 19
    return out


def inspector(x, y, w, h, user, repos):
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{PANEL}"/>'] + tabs(x, y, w, ["Inspector"], "Inspector")
    cc = user["contributionsCollection"]
    langs = {}
    for r in repos:
        if r["name"] == user["login"]:
            continue
        for e in r["languages"]["edges"]:
            n = e["node"]["name"]
            langs.setdefault(n, [0, e["node"]["color"] or TEXT2])[0] += e["size"]
    total = sum(v[0] for v in langs.values()) or 1
    top = sorted(langs.items(), key=lambda kv: -kv[1][0])[:4]
    cy = y + 26 + 8
    out.append(icon("box", x + 10, cy + 2, 16, ACCENT))
    out.append(text(x + 32, cy + 10, user["login"], 13, TEXT, weight=500))
    cy += 26

    def component(title, rows):
        nonlocal cy
        out.append(f'<rect x="{x + 6}" y="{cy}" width="{w - 12}" height="20" rx="3" fill="{RAISED}"/>')
        out.append(icon("down", x + 10, cy + 4, 12, TEXT2))
        out.append(text(x + 26, cy + 10, title, 12, TEXT, weight=500))
        cy += 24
        for label, value in rows:
            out.append(text(x + 14, cy + 9, label, 12, TEXT2))
            out.append(f'<rect x="{x + w - 118}" y="{cy}" width="110" height="18" rx="3" fill="{FIELD}"/>')
            out.append(text(x + w - 112, cy + 9, value, 12, TEXT))
            cy += 19
        cy += 3

    component("Contributions", [("Past year", f"{cc['contributionCalendar']['totalContributions']:,}"),
                                ("Commits", f"{cc['totalCommitContributions']:,}")])
    component("Repositories", [("Public", str(len(repos))),
                               ("Stars", str(sum(r["stargazerCount"] for r in repos)))])
    out.append(f'<rect x="{x + 6}" y="{cy}" width="{w - 12}" height="20" rx="3" fill="{RAISED}"/>')
    out.append(icon("down", x + 10, cy + 4, 12, TEXT2))
    out.append(text(x + 26, cy + 10, "Languages", 12, TEXT, weight=500))
    cy += 24
    bx, bw = x + 14, w - 28
    out.append(f'<clipPath id="kbar"><rect x="{bx}" y="{cy}" width="{bw}" height="8" rx="4"/></clipPath>')
    out.append(f'<g clip-path="url(#kbar)"><rect x="{bx}" y="{cy}" width="{bw}" height="8" fill="{FIELD}"/>')
    lx = bx
    for name, (size, color) in top:
        lw = bw * size / total
        out.append(f'<rect x="{lx:.1f}" y="{cy}" width="{lw:.1f}" height="8" fill="{color}"/>')
        lx += lw
    out.append("</g>")
    cy += 14
    for i, (name, (size, color)) in enumerate(top):
        cx = bx + (i % 2) * (bw / 2)
        ly = cy + (i // 2) * 17
        out.append(f'<circle cx="{cx + 4}" cy="{ly + 7}" r="4" fill="{color}"/>')
        out.append(text(cx + 13, ly + 7, f"{name} {100 * size / total:.1f}%", 11, TEXT2))
    return out


def embed(svg, x, y, w, h):
    """Another SVG placed in the box, its own styles and animation kept."""
    svg = re.sub(r"<\?xml[^>]*\?>", "", svg).strip()
    m = re.match(r"<svg\b([^>]*)>", svg)
    if not m:
        return []
    vb = re.search(r'viewBox="([^"]+)"', m.group(1))
    if not vb:
        sw, sh = (re.search(rf'{a}="([\d.]+)', m.group(1)).group(1) for a in ("width", "height"))
        vb = f"0 0 {sw} {sh}"
    else:
        vb = vb.group(1)
    return [f'<svg x="{x}" y="{y}" width="{w}" height="{h}" viewBox="{vb}" preserveAspectRatio="xMidYMid meet">'
            + svg[m.end():]]


def timeline(x, y, w, h, user, snake):
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{PANEL}"/>'] + tabs(x, y, w, ["Timeline"], "Timeline")
    total = user["contributionsCollection"]["contributionCalendar"]["totalContributions"]
    out.append(text(x + w - 10, y + 13, f"{total:,} contributions in the past year", 11, TEXT2, "end"))
    if snake:
        out += embed(snake, x + 10, y + 32, w - 20, h - 38)
    return out


def render(user, snake):
    repos = user["repositories"]["nodes"]
    top, ph, th = 0, 270, 180
    parts = [f'<rect width="{W}" height="{ph + 4 + th}" fill="{GAP}"/>']
    parts += hierarchy(0, top, 240, ph, user, repos)
    parts += console(244, top, 432, ph, user, repos)
    parts += inspector(680, top, 320, ph, user, repos)
    parts += timeline(0, top + ph + 4, W, th, user, snake)
    h = ph + 4 + th
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}">'
            f'<title>{escape(user["login"])} in the editor: repositories, latest commits, stats and contributions</title>'
            + "".join(parts) + "</svg>")


if __name__ == "__main__":
    snake_path, out_path = sys.argv[1], sys.argv[2]
    if os.environ.get("EDITOR_DATA"):  # a saved reply, to draw without asking GitHub
        user = json.load(open(os.environ["EDITOR_DATA"]))
    else:
        user = fetch(os.environ["LOGIN"], os.environ["GITHUB_TOKEN"])
    snake = open(snake_path).read() if os.path.exists(snake_path) else ""
    open(out_path, "w").write(render(user, snake))
