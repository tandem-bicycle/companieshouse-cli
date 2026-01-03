
import curses
import textwrap
from companies_house_api import CompaniesHouseAPI

def draw_frame(stdscr, title, help_text):
    # ... (this function remains the same)
    h, w = stdscr.getmaxyx()
    stdscr.clear()
    
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK) # Unselected Tab

    # New colors for bar chart
    curses.init_pair(5, curses.COLOR_GREEN, curses.COLOR_BLACK) # Lower bound
    curses.init_pair(6, curses.COLOR_YELLOW, curses.COLOR_BLACK) # Upper range

    stdscr.attron(curses.color_pair(1))
    stdscr.box()
    stdscr.attroff(curses.color_pair(1))

    stdscr.addstr(0, 2, f" {title} ", curses.color_pair(1))

    stdscr.attron(curses.color_pair(3))
    stdscr.addstr(h - 1, 1, help_text.ljust(w - 2))
    stdscr.attroff(curses.color_pair(3))

    stdscr.refresh( )
    
    if h - 3 < 3 or w - 2 < 5:
        stdscr.clear()
        stdscr.addstr(0, 0, "Terminal too small. Please resize.")
        stdscr.refresh()
        return None # Indicate that content_win could not be created

    content_win = stdscr.derwin(h - 3, w - 2, 2, 1)
    return content_win

def show_status_message(stdscr, message):
    # ... (this function remains the same)
    h, w = stdscr.getmaxyx()
    x = w//2 - len(message)//2
    y = h//2
    stdscr.addstr(y, x, message)
    stdscr.refresh()

def select_from_list(stdscr, items, title):
    """Scrollable list selection TUI component. Returns selected item or navigation signal."""
    help_text = "↑/↓ Navigate | ↵ Select | q New Search"
    content_win = draw_frame(stdscr, title, help_text)
    if content_win is None:
        return None # Terminal too small
    h, w = content_win.getmaxyx()
    current_row = 0
    scroll_pos = 0
    
    while True:
        content_win.clear()
        
        # Calculate viewport
        visible_items = items[scroll_pos : scroll_pos + h]
        
        for idx, item in enumerate(visible_items):
            actual_idx = scroll_pos + idx
            truncated_item = item[:w-3]

            if actual_idx == current_row:
                content_win.attron(curses.color_pair(2))
                content_win.addstr(idx, 2, truncated_item)
                content_win.attroff(curses.color_pair(2))
            else:
                content_win.addstr(idx, 2, truncated_item)
        content_win.refresh()

        key = stdscr.getch()
        if key == ord('q'): return "BACK_TO_NEW_SEARCH"
        elif key == curses.KEY_UP:
            if current_row > 0:
                current_row -= 1
                if current_row < scroll_pos:
                    scroll_pos = current_row
        elif key == curses.KEY_DOWN:
            if current_row < len(items) - 1:
                current_row += 1
                if current_row >= scroll_pos + h:
                    scroll_pos = current_row - h + 1
        elif key == curses.KEY_ENTER or key in [10, 13]:
            return items[current_row]

def display_tabbed_viewer(stdscr, tab_data, title):
    """A text viewer with a correctly implemented horizontal tabbed interface. Returns navigation signal."""
    help_text = "←/→ Switch Tabs | ↑/↓ Scroll | b Back to List | q New Search"
    content_win = draw_frame(stdscr, title, help_text)
    if content_win is None:
        return None # Terminal too small
    h, w = content_win.getmaxyx()
    
    tab_names = list(tab_data.keys())
    current_tab = 0
    pads = {}
    pad_pos = {}

    for tab_name, content in tab_data.items():
        lines = content.split('\n')
        wrapped_lines = []
        for line in lines:
            wrapped_lines.extend(textwrap.wrap(line, w - 4, replace_whitespace=False, drop_whitespace=False))
        
        pad = curses.newpad(max(1, len(wrapped_lines)), w)
        pad.keypad(True)
        for i, line in enumerate(wrapped_lines):
            pad.addstr(i, 0, line)
        pads[tab_name] = pad
        pad_pos[tab_name] = 0

    while True:
        content_win.clear()
        
        x_pos = 2
        for i, name in enumerate(tab_names):
            if i == current_tab:
                content_win.attron(curses.color_pair(2))
                content_win.addstr(0, x_pos, f" {name} ")
                content_win.attroff(curses.color_pair(2))
            else:
                content_win.attron(curses.color_pair(4))
                content_win.addstr(0, x_pos, f" {name} ")
                content_win.attroff(curses.color_pair(4))
            x_pos += len(name) + 4
        
        content_win.addstr(1, 1, "=" * (w - 2), curses.color_pair(1))
        content_win.refresh()

        current_pad = pads[tab_names[current_tab]]
        max_scroll = max(0, current_pad.getmaxyx()[0] - (h - 2))

        current_pad.refresh(pad_pos[tab_names[current_tab]], 0, 4, 3, h, w-1) 

        key = stdscr.getch()

        if key == ord('q'): return "BACK_TO_NEW_SEARCH"
        elif key == ord('b'): return "BACK_TO_LIST"
        elif key == curses.KEY_LEFT:
            current_tab = (current_tab - 1 + len(tab_names)) % len(tab_names)
            pad_pos[tab_names[current_tab]] = 0
        elif key == curses.KEY_RIGHT:
            current_tab = (current_tab + 1) % len(tab_names)
            pad_pos[tab_names[current_tab]] = 0
        elif key == curses.KEY_UP:
            pad_pos[tab_names[current_tab]] = max(0, pad_pos[tab_names[current_tab]] - 1)
        elif key == curses.KEY_DOWN:
            pad_pos[tab_names[current_tab]] = min(max_scroll, pad_pos[tab_names[current_tab]] + 1)

def parse_control_percentages(natures):
    # ... (this function remains the same) ...
    voting_lower, voting_upper = 0, 0
    shares_lower, shares_upper = 0, 0

    control_ranges = {
        "75-to-100-percent": (75, 100),
        "50-to-75-percent": (50, 75),
        "25-to-50-percent": (25, 50),
        "10-to-25-percent": (10, 25)
    }

    for nature in natures:
        for key_phrase, (lower, upper) in control_ranges.items():
            if key_phrase in nature:
                if "voting-rights" in nature:
                    if lower > voting_lower: voting_lower = lower
                    if upper > voting_upper: voting_upper = upper
                elif "ownership-of-shares" in nature:
                    if lower > shares_lower: shares_lower = lower
                    if upper > shares_upper: shares_upper = upper
    
    return (voting_lower, voting_upper), (shares_lower, shares_upper)


def main(stdscr):
    """Main function to run the TUI application with full navigation."""
    curses.curs_set(0)

    # Outer loop for new searches
    while True:
        # --- Step 1: Get User Input ---
        help_text = "↵ Enter | Ctrl+C Quit"
        input_win = draw_frame(stdscr, "Companies House Search", help_text)
        if input_win is None:
            stdscr.getch() # Wait for user to acknowledge "Terminal too small"
            break # Exit the main loop to terminate the program
        input_win.addstr(1, 2, "Enter company name to search: ")
        curses.echo()
        curses.curs_set(1)
        search_query = input_win.getstr(3, 2, 60).decode('utf-8')
        curses.noecho()
        curses.curs_set(0)

        if not search_query.strip(): return # Exit app if no query

        try:
            client = CompaniesHouseAPI()
        except ValueError as e:
            input_win.addstr(5, 2, f"API Key Error: {e}. Press any key to exit.")
            stdscr.getch()
            return # Exit app

        search_results_cache = None # Cache search results for 'back to list'

        # Inner loop for viewing search results and company details
        while True:
            if search_results_cache:
                search_results = search_results_cache
                search_results_cache = None # Clear cache after use
            else:
                show_status_message(stdscr, "Searching...")
                search_results = client.search_companies(search_query)
            
            if not search_results or not search_results.get('items'):
                show_status_message(stdscr, f"No companies found for '{search_query}'. Press any key for new search.")
                stdscr.getch()
                break # Break inner loop -> go to outer loop (new search)
            
            menu_items = [f"{item.get('title')} ({item.get('company_number')})" for item in search_results['items']]
            
            # Call select_from_list, which now returns a navigation signal or selected item
            selected_list_result = select_from_list(stdscr, menu_items, "Search Results")
            
            if selected_list_result == "BACK_TO_NEW_SEARCH":
                break # Break inner loop -> go to outer loop (new search)
            elif selected_list_result is None: # User pressed q or nothing in select_from_list and exited
                return # Exit app
            
            company_number = selected_list_result.split('(')[-1].replace(')', '')

            # --- Step 3: Fetch Data and Prepare Tab Content ---
            show_status_message(stdscr, "Fetching details...")
            profile = client.get_company_profile(company_number)
            filing = client.get_filing_history(company_number)
            pscs = client.get_persons_with_significant_control(company_number)
            
            # --- Profile Tab ---
            profile_content = ""
            if profile:
                profile_content += f"Name:     {profile.get('company_name')}\n"
                profile_content += f"Status:   {profile.get('company_status')}\n"
                address = profile.get('registered_office_address', {})
                profile_content += f"Address:  {address.get('address_line_1')}, {address.get('postal_code')}\n"
            else:
                profile_content = "No profile data found."

            # --- Filing History Tab ---
            filing_content = ""
            if filing and filing.get('items'):
                for item in filing['items']:
                    marker = ""
                    description_lower = item.get('description', '').lower()
                    if "dormant" in description_lower or "active" in description_lower:
                        marker = "*** STATUS CHANGE *** "
                    
                    filing_content += f"{marker}Date: {item.get('date', 'N/A')}\n"
                    filing_content += f"  Desc: {item.get('description', 'N/A')}\n"
                    filing_content += f"  Type: {item.get('type', 'N/A')}\n\n"
            else:
                filing_content = "No filing history found."

            # --- PSCs Tab (with dual bar charts) ---
            pscs_content = ""
            if pscs and pscs.get('items'):
                for psc in pscs['items']:
                    name = psc.get('name', 'N/A')
                    status = "Ceased" if psc.get('ceased_on') else "Active"
                    natures = psc.get('natures_of_control', [])
                    
                    (voting_lower, voting_upper), (shares_lower, shares_upper) = parse_control_percentages(natures)
                    
                    # If ceased, set percentages to 0 to reflect no current control
                    if status == "Ceased":
                        voting_lower, voting_upper = 0, 0
                        shares_lower, shares_upper = 0, 0
                    
                    # Bar chart dimensions
                    bar_len_scale = 10 # 1 char for every 10%
                    
                    # Voting Bar
                    voting_bar_lower_len = voting_lower // bar_len_scale
                    voting_bar_range_len = (voting_upper - voting_lower) // bar_len_scale
                    
                    # Shares Bar
                    shares_bar_lower_len = shares_lower // bar_len_scale
                    shares_bar_range_len = (shares_upper - shares_lower) // bar_len_scale
                    
                    pscs_content += f"- Name:    {name}\n"
                    pscs_content += f"  Status:  {status}\n"
                    
                    # Display Voting Bar
                    pscs_content += "  Voting:  "
                    if voting_lower > 0:
                        pscs_content += '█' * voting_bar_lower_len
                    if voting_upper > voting_lower:
                        pscs_content += '▓' * voting_bar_range_len
                    pscs_content += f" ({voting_lower}-{voting_upper}%)".ljust(20) + "\n" # Ensure consistent length
                    
                    # Display Shares Bar
                    pscs_content += "  Shares:  "
                    if shares_lower > 0:
                        pscs_content += '█' * shares_bar_lower_len
                    if shares_upper > shares_lower:
                        pscs_content += '▓' * shares_bar_range_len
                    pscs_content += f" ({shares_lower}-{shares_upper}%)".ljust(20) + "\n"
                    
                    pscs_content += f"  Natures: {', '.join(natures)}\n\n"
            else:
                pscs_content = "No Persons with Significant Control found or company is exempt."

            tab_data = {
                "Profile": profile_content,
                "Filing History": filing_content,
                "PSCs": pscs_content
            }

            display_tabbed_viewer_result = display_tabbed_viewer(stdscr, tab_data, f"Details for {company_number}")
            
            if display_tabbed_viewer_result == "BACK_TO_NEW_SEARCH":
                break # Break inner loop -> go to outer loop (new search)
            elif display_tabbed_viewer_result == "BACK_TO_LIST":
                search_results_cache = search_results # Store current search results
                continue # Continue inner loop -> go back to select_from_list
            elif display_tabbed_viewer_result is None: # User pressed q from tabbed viewer to exit
                return # Exit app

if __name__ == "__main__":
    curses.wrapper(main)
