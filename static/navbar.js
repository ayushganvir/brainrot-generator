document.addEventListener('DOMContentLoaded', () => {
    const nav = document.createElement('nav');
    nav.style.cssText = `
        background: rgba(0, 0, 0, 0.8);
        backdrop-filter: blur(10px);
        padding: 1rem 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 2rem;
    `;

    const logo = document.createElement('div');
    logo.innerHTML = '<span style="font-size: 1.5rem;">🎬</span> <span style="font-weight: bold; color: white;">ContentGen</span>';
    
    const links = document.createElement('div');
    links.style.display = 'flex';
    links.style.gap = '2rem';

    const createLink = (text, href, isActive) => {
        const a = document.createElement('a');
        a.href = href;
        a.textContent = text;
        a.style.cssText = `
            color: ${isActive ? '#3498db' : 'rgba(255, 255, 255, 0.7)'};
            text-decoration: none;
            font-weight: 500;
            transition: color 0.2s;
        `;
        a.onmouseover = () => a.style.color = '#3498db';
        a.onmouseout = () => a.style.color = isActive ? '#3498db' : 'rgba(255, 255, 255, 0.7)';
        return a;
    };

    const currentPath = window.location.pathname;
    links.appendChild(createLink('Script Mode', '/script', currentPath === '/script'));
    links.appendChild(createLink('Instagram Manager', '/instagram', currentPath === '/instagram'));

    nav.appendChild(logo);
    nav.appendChild(links);

    document.body.insertBefore(nav, document.body.firstChild);
});
