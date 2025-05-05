// API Configuration
const apiBaseUrl = "http://localhost:8000";

// DOM Elements
const authStatus = document.getElementById('auth-status');
const authForm = document.getElementById('auth-user-form');
const createUserForm = document.getElementById('create-user-form');
const updateUserForm = document.getElementById('update-user-form');
const deleteUserForm = document.getElementById('delete-user-form');
const userList = document.getElementById('user-list');
const userMeDetails = document.getElementById('user-me-details');

// Helper Functions
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification ${type} show`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
        ${message}
    `;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

function setAuthStatus(authenticated) {
    if (authenticated) {
        authStatus.textContent = 'Authenticated';
        authStatus.classList.remove('error');
        authStatus.classList.add('authenticated');
    } else {
        authStatus.textContent = 'Not authenticated';
        authStatus.classList.remove('authenticated');
        authStatus.classList.add('error');
    }
}

function openTab(tabId) {
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.style.display = 'none';
    });
    
    // Remove active class from all tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show the selected tab content
    document.getElementById(tabId).style.display = 'block';
    
    // Add active class to the clicked button
    event.currentTarget.classList.add('active');
}

// Authentication
authForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('auth_username').value;
    const password = document.getElementById('auth_password').value;
    
    try {
        const response = await fetch(`${apiBaseUrl}/token`, {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body: new URLSearchParams({
                username: username,
                password: password,
                grant_type: "password"
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            localStorage.setItem('token', data.access_token);
            setAuthStatus(true);
            showNotification('Login successful!', 'success');
            fetchUserme();
            fetchUsers();
        } else {
            setAuthStatus(false);
            showNotification(data.detail || 'Login failed', 'error');
        }
    } catch (error) {
        setAuthStatus(false);
        showNotification('Network error during login', 'error');
        console.error('Login error:', error);
    }
});

// User Management
async function fetchUsers() {
    try {
        const response = await fetch(`${apiBaseUrl}/users/`, {
            method: "GET",
            headers: { 
                "Authorization": `Bearer ${localStorage.getItem("token")}`
            }
        });
        
        if (!response.ok) throw new Error('Failed to fetch users');
        
        const users = await response.json();
        
        userList.innerHTML = users.length > 0 
            ? users.map(user => `
                <div class="user-item">
                    <span>${user.username} <small>(ID: ${user.id})</small></span>
                    <small>${user.email}</small>
                </div>
            `).join('')
            : '<p>No users found</p>';
        
    } catch (error) {
        userList.innerHTML = '<p>Error loading users</p>';
        console.error('Fetch users error:', error);
    }
}

async function fetchUserme() {
    if (!localStorage.getItem('token')) {
        userMeDetails.innerHTML = '<p>Please login to view your details</p>';
        return;
    }
    
    try {
        const response = await fetch(`${apiBaseUrl}/users/me`, {
            method: "GET",
            headers: { 
                "Authorization": `Bearer ${localStorage.getItem("token")}`
            }
        });
        
        if (!response.ok) throw new Error('Failed to fetch user data');
        
        const user = await response.json();
        
        userMeDetails.innerHTML = `
            <div class="user-detail">
                <span>Username:</span>
                <span>${user.username}</span>
            </div>
            <div class="user-detail">
                <span>Email:</span>
                <span>${user.email}</span>
            </div>
            <div class="user-detail">
                <span>Full Name:</span>
                <span>${user.full_name || 'Not specified'}</span>
            </div>
            <div class="user-detail">
                <span>User ID:</span>
                <span>${user.id}</span>
            </div>
        `;
        
    } catch (error) {
        userMeDetails.innerHTML = '<p>Error loading user data</p>';
        console.error('Fetch user me error:', error);
    }
}

createUserForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const formData = {
        username: document.getElementById('username').value,
        email: document.getElementById('email').value,
        full_name: document.getElementById('full_name').value,
        password: document.getElementById('password').value
    };
    
    try {
        const response = await fetch(`${apiBaseUrl}/register/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showNotification('User created successfully!', 'success');
            createUserForm.reset();
            fetchUsers();
        } else {
            showNotification(data.detail || 'Error creating user', 'error');
        }
    } catch (error) {
        showNotification('Network error during user creation', 'error');
        console.error('Create user error:', error);
    }
});

updateUserForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const userId = document.getElementById('update-user-id').value;
    const formData = {
        username: document.getElementById('update-username').value,
        email: document.getElementById('update-email').value,
        full_name: document.getElementById('update-full_name').value,
        password: document.getElementById('update-password').value
    };
    
    // Remove empty fields
    Object.keys(formData).forEach(key => {
        if (formData[key] === '') delete formData[key];
    });
    
    try {
        const response = await fetch(`${apiBaseUrl}/users/${userId}`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${localStorage.getItem("token")}`
            },
            body: JSON.stringify(formData)
        });
        
        if (response.ok) {
            showNotification('User updated successfully!', 'success');
            updateUserForm.reset();
            fetchUsers();
            fetchUserme();
        } else {
            const data = await response.json();
            showNotification(data.detail || 'Error updating user', 'error');
        }
    } catch (error) {
        showNotification('Network error during user update', 'error');
        console.error('Update user error:', error);
    }
});

deleteUserForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const userId = document.getElementById('delete-user-id').value;
    
    if (!confirm(`Are you sure you want to delete user with ID ${userId}?`)) {
        return;
    }
    
    try {
        const response = await fetch(`${apiBaseUrl}/users/${userId}`, {
            method: "DELETE",
            headers: { 
                "Authorization": `Bearer ${localStorage.getItem("token")}`
            }
        });
        
        if (response.ok) {
            showNotification('User deleted successfully!', 'success');
            deleteUserForm.reset();
            fetchUsers();
        } else {
            const data = await response.json();
            showNotification(data.detail || 'Error deleting user', 'error');
        }
    } catch (error) {
        showNotification('Network error during user deletion', 'error');
        console.error('Delete user error:', error);
    }
});

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setAuthStatus(!!localStorage.getItem('token'));
    fetchUsers();
    
    if (localStorage.getItem('token')) {
        fetchUserme();
    }
});