
import requests
from html.parser import HTMLParser


class CoordinateTableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_table = False
        self.in_row = False
        self.in_cell = False
        self.current_cell = ""
        self.rows = []
        self.current_row = []

    def handle_starttag(self, tag, attrs):
        if tag == 'table':
            self.in_table = True
        elif tag == 'tr' and self.in_table:
            self.in_row = True
            self.current_row = []
        elif tag == 'td' and self.in_row:
            self.in_cell = True
            self.current_cell = ""

    def handle_endtag(self, tag):
        if tag == 'td' and self.in_cell:
            self.in_cell = False
            text = self.current_cell.replace('\xa0', ' ').strip()
            self.current_row.append(text)
        elif tag == 'tr' and self.in_row:
            self.in_row = False
            if self.current_row:
                self.rows.append(self.current_row)
        elif tag == 'table':
            self.in_table = False

    def handle_data(self, data):
        if self.in_cell:
            self.current_cell += data

    def get_coordinate_data(self):
        if not self.rows or len(self.rows) < 2:
            return []

        # Skip header row
        data = []
        for row in self.rows[1:]:
            if len(row) >= 3:
                try:
                    x = int(row[0])
                    char = row[1] if row[1] else ' '
                    y = int(row[2])
                    data.append((x, y, char))
                except ValueError:
                    continue
        return data

def render_ascii_art(coords):
    if not coords:
        return None

    # Find bounds
    xs = [p[0] for p in coords]
    ys = [p[1] for p in coords]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    width = max_x - min_x + 1
    height = max_y - min_y + 1

    # Create grid
    grid = [[' ' for _ in range(width)] for _ in range(height)]

    # Fill grid
    for x, y, char in coords:
        grid_x = x - min_x
        grid_y = max_y - y  # flip Y-axis
        if 0 <= grid_x < width and 0 <= grid_y < height:
            grid[grid_y][grid_x] = char


    # Convert to string
    return '\n'.join(''.join(row) for row in grid)

def fetch_and_render(url):
    try:
        print(f"Fetching: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error: {e}")
        return

    parser = CoordinateTableParser()
    parser.feed(response.text)
    coords = parser.get_coordinate_data()

    if not coords:
        print("No valid coordinate data found.")
        return

    art = render_ascii_art(coords)
    if art:
        print("\n" + "="*50)
        print("RENDERED ASCII ART")
        print("="*50)
        print(art)
        print("="*50)
    else:
        print("Failed to render ASCII art.")

def main():
    url = input("Enter the published Google Docs URL: ").strip()
    fetch_and_render(url)


if __name__ == "__main__":
    main()