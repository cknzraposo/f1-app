const root = document.documentElement;
const statusMessage = document.getElementById('site-status');
const themeToggle = document.getElementById('theme-toggle');
const menu = document.getElementById('course-menu');
const searchDialog = document.getElementById('lesson-search');
const searchInput = document.getElementById('mkdocs-search-query');

function applyTheme(theme) {
    root.dataset.theme = theme;
    themeToggle.textContent = theme === 'dark' ? 'Light mode' : 'Dark mode';
    themeToggle.setAttribute('aria-label', `Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`);
}

try {
    applyTheme(localStorage.getItem('f1-workshop-theme') === 'light' ? 'light' : 'dark');
} catch (error) {
    console.warn('Theme preference could not be read.', error);
    statusMessage.textContent = 'Browser storage is unavailable. Using the default racing theme.';
}

themeToggle.addEventListener('click', () => {
    const theme = root.dataset.theme === 'dark' ? 'light' : 'dark';
    applyTheme(theme);
    try {
        localStorage.setItem('f1-workshop-theme', theme);
    } catch (error) {
        console.warn('Theme preference could not be saved.', error);
        statusMessage.textContent = 'Theme changed for this page only. Browser storage is unavailable.';
    }
});

const narrowScreen = matchMedia('(max-width: 960px)');
function updateMenu() {
    menu.open = !narrowScreen.matches;
}
updateMenu();
narrowScreen.addEventListener('change', updateMenu);

function openSearch() {
    if (!searchDialog.open) searchDialog.showModal();
    searchInput.focus();
}

document.querySelector('[data-open-search]').addEventListener('click', openSearch);
document.querySelector('[data-close-search]').addEventListener('click', () => searchDialog.close());
searchDialog.addEventListener('click', event => {
    if (event.target === searchDialog) {
        const bounds = searchDialog.getBoundingClientRect();
        if (event.clientX < bounds.left || event.clientX > bounds.right ||
            event.clientY < bounds.top || event.clientY > bounds.bottom) {
            searchDialog.close();
        }
    }
});

document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && searchDialog.open) {
        event.preventDefault();
        searchDialog.close();
        return;
    }
    const target = event.target;
    const editing = target instanceof HTMLElement &&
        (target.isContentEditable || target.closest('input, textarea, select'));
    if (event.key === '/' && !event.ctrlKey && !event.metaKey && !event.altKey && !editing) {
        event.preventDefault();
        openSearch();
    }
});

document.querySelectorAll('pre > code').forEach(code => {
    const pre = code.parentElement;
    const panel = document.createElement('div');
    panel.className = 'code-panel';
    pre.before(panel);
    panel.append(pre);

    const button = document.createElement('button');
    button.className = 'copy-code';
    button.type = 'button';
    button.textContent = 'Copy';
    button.setAttribute('aria-label', 'Copy code example');
    panel.append(button);
    button.addEventListener('click', async () => {
        if (!navigator.clipboard) {
            button.textContent = 'Select code to copy';
            statusMessage.textContent = 'Clipboard access is unavailable. Select and copy the code manually.';
            return;
        }
        try {
            await navigator.clipboard.writeText(code.textContent);
            button.textContent = 'Copied';
            statusMessage.textContent = 'Code example copied.';
            setTimeout(() => { button.textContent = 'Copy'; }, 2500);
        } catch (error) {
            console.error('Code example could not be copied.', error);
            button.textContent = 'Select code to copy';
            statusMessage.textContent = 'Copy failed. Select and copy the code manually.';
        }
    });
});
