document.getElementById('start-scraping').addEventListener('click', () => {
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    chrome.scripting.executeScript({
      target: { tabId: tabs[0].id },
      files: ['content.js']
    });
  });
});

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'profiles') {
    const profileList = document.getElementById('profile-list');
    profileList.innerHTML = '';
    message.profiles.forEach((profile, index) => {
      const li = document.createElement('li');
      li.textContent = `${profile.name} (${profile.url})`;
      
      const checkbox = document.createElement('input');
      checkbox.type = 'checkbox';
      checkbox.id = `profile-${index}`;
      checkbox.value = profile.url;
      
      li.prepend(checkbox);
      profileList.appendChild(li);
    });

    const scrapeButton = document.createElement('button');
    scrapeButton.textContent = 'Scrape Selected Profiles';
    scrapeButton.addEventListener('click', () => {
      const selectedProfiles = [];
      document.querySelectorAll('input[type="checkbox"]:checked').forEach(checkbox => {
        selectedProfiles.push(checkbox.value);
      });

      const logContainer = document.getElementById('log-container');
      logContainer.innerHTML = '';

      selectedProfiles.forEach(url => {
        const logEntry = document.createElement('p');
        logEntry.textContent = `Scraping: ${url}`;
        logContainer.appendChild(logEntry);

        fetch('http://localhost:5000/scrape', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ url: url })
        })
        .then(response => response.json())
        .then(data => {
          const successEntry = document.createElement('p');
          successEntry.textContent = `Success: ${url}`;
          logContainer.appendChild(successEntry);
          console.log('Success:', data);
        })
        .catch(error => {
          const errorEntry = document.createElement('p');
          errorEntry.textContent = `Error: ${url}`;
          logContainer.appendChild(errorEntry);
          console.error('Error:', error);
        });
      });
    });

    profileList.appendChild(scrapeButton);
  }
});
