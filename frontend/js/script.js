document.addEventListener('DOMContentLoaded', () => {
    // Get references to the HTML elements
    const itemForm = document.getElementById('item-form');
    const itemInput = document.getElementById('item-input');
    const itemList = document.getElementById('item-list');

    // Function to create a new list item
    function addItem(e) {
        // Prevent the form from submitting and reloading the page
        e.preventDefault();

        const newItemText = itemInput.value.trim();

        if (newItemText === '') {
            alert('Please enter an item.');
            return;
        }

        // Create new list item (li)
        const li = document.createElement('li');

        // Create text node for the item
        const itemText = document.createTextNode(newItemText);
        li.appendChild(itemText);

        // Create delete button
        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'delete-btn';
        deleteBtn.appendChild(document.createTextNode('X'));
        li.appendChild(deleteBtn);

        // Add the new item to the list
        itemList.appendChild(li);

        // Clear the input field
        itemInput.value = '';
    }

    // Function to handle item clicks (delete or mark as complete)
    function handleItemClick(e) {
        // Check if the delete button was clicked
        if (e.target.classList.contains('delete-btn')) {
            if (confirm('Are you sure you want to delete this item?')) {
                const li = e.target.parentElement;
                itemList.removeChild(li);
            }
        }
        // Otherwise, toggle the 'completed' class on the list item
        else if (e.target.tagName === 'LI') {
            e.target.classList.toggle('completed');
        }
    }


    // --- Event Listeners ---

    // Listen for form submission
    itemForm.addEventListener('submit', addItem);

    // Listen for clicks on the item list (for deleting and completing items)
    itemList.addEventListener('click', handleItemClick);
});
