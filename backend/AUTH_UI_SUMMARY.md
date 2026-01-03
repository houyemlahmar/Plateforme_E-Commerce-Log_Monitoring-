# 🔐 Authentication UI - Login & Profile Interface

## ✅ Successfully Created

Complete authentication UI has been implemented with login and profile pages!

## 🌐 Access the Application

**Server is running on: http://localhost:5001**

### Main URLs:

1. **Login Page**: http://localhost:5001/login
   - Beautiful, modern login interface
   - Register new accounts
   - Secure authentication

2. **Profile Page**: http://localhost:5001/profile  
   - User profile information
   - Role-based quick access links
   - Account details

3. **Dashboard**: http://localhost:5001/dashboard
   - Analytics dashboard (requires auth)

4. **API Endpoints**: http://localhost:5001/api/auth/
   - `/api/auth/login` - Login
   - `/api/auth/register` - Register
   - `/api/auth/me` - Current user info

## 🔑 Test Credentials

### Admin Account
- **Username**: `admin`
- **Password**: `admin12345`
- **Role**: admin (full access)

### Sample Users
- **Analyst**: `analyst_demo` / `analyst123`
- **Moderator**: `moderator_demo` / `moderator123`
- **Viewer**: `viewer_demo` / `viewer123`

## 📋 How to Use

### 1. Login
1. Open http://localhost:5001/login in your browser
2. Enter username and password
3. Click "Login"
4. You'll be redirected to your profile page

### 2. View Profile
- After logging in, you'll see:
  - Your avatar
  - Username and email
  - Role badge (color-coded)
  - Account details (ID, status, created date, last login)
  - Quick access links (based on your role)

### 3. Access Features
Click on the quick access cards to navigate to:
- **Dashboard** - View analytics (all roles)
- **Search Logs** - Search log data (all roles)
- **Analytics** - Detailed analytics (analyst+)
- **Upload Logs** - Upload files (analyst+)
- **User Management** - Manage users (admin only)

## 🎨 UI Features

### Login Page
- ✅ Modern, responsive design
- ✅ Gradient purple theme
- ✅ Login and registration forms
- ✅ Form validation
- ✅ Success/error alerts
- ✅ Loading indicators
- ✅ Auto-redirect if already logged in

### Profile Page
- ✅ Beautiful navbar with navigation
- ✅ User avatar with initial
- ✅ Color-coded role badges
  - 🔴 Admin (red)
  - 🟢 Moderator (teal)
  - 🔵 Analyst (blue)
  - ⚪ Viewer (gray)
- ✅ Account details grid
- ✅ Role-based quick access cards
- ✅ Logout functionality

## 🔒 Security Features

### Token Management
- Tokens stored in browser localStorage
- Auto-logout on expired tokens
- Token validation on protected pages
- Secure password transmission (HTTPS recommended for production)

### Role-Based Access
Different quick links shown based on role:
- **Viewer**: Dashboard, Search
- **Analyst**: + Analytics, Upload
- **Moderator**: All analyst features
- **Admin**: + User Management

## 🧪 Testing Authentication

### Using Browser
1. Open http://localhost:5001/login
2. Log in with admin/admin12345
3. Check profile page shows admin role
4. Try accessing protected routes

### Using PowerShell
```powershell
# Test login
$response = Invoke-RestMethod -Uri "http://localhost:5001/api/auth/login" `
    -Method Post `
    -Body (@{username="admin"; password="admin12345"} | ConvertTo-Json) `
    -ContentType "application/json"

Write-Host "User: $($response.user.username)"
Write-Host "Role: $($response.user.role)"

# Use token for protected routes
$token = $response.access_token
$headers = @{Authorization="Bearer $token"}
Invoke-RestMethod -Uri "http://localhost:5001/api/auth/me" -Headers $headers
```

### Using cURL
```bash
# Login
curl -X POST http://localhost:5001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin12345"}'

# Access protected route (replace TOKEN)
curl http://localhost:5001/api/auth/me \
  -H "Authorization: Bearer TOKEN"
```

## 📁 Files Created/Modified

### New Templates
1. `backend/app/templates/login.html` - Login & registration page
2. `backend/app/templates/profile.html` - User profile page

### Modified Files
1. `backend/run_server.py` - Updated to port 5001
2. `backend/app/__init__.py` - Added login/profile routes

## 🎯 Current Status

✅ **Server Running**: http://localhost:5001  
✅ **MongoDB**: Connected  
✅ **Elasticsearch**: Connected  
✅ **Redis**: Connected  
✅ **Authentication**: Working  
✅ **Login UI**: Created  
✅ **Profile UI**: Created  

## 🚀 Next Steps

1. **Open Browser**: Navigate to http://localhost:5001/login
2. **Login as Admin**: Use admin/admin12345
3. **Explore Profile**: View your profile and quick access links
4. **Test Protected Routes**: Try accessing dashboard and other features
5. **Create New Users**: Use registration form to create test accounts

## 📝 Notes

- Port changed from 5000 to **5001** as requested
- All existing API routes still work on port 5001
- Protected routes now require authentication
- Beautiful, modern UI with responsive design
- Token-based authentication with localStorage
- Role hierarchy properly implemented

## 🔧 Troubleshooting

### Can't access login page
- Ensure Flask is running on port 5001
- Check http://localhost:5001/health to verify server is up

### Login fails
- Verify credentials match test accounts above
- Check MongoDB is connected
- Check browser console for errors

### Token expired
- Click logout and login again
- Tokens expire after 1 hour
- Use refresh token endpoint to get new access token

## 🎉 Ready to Use!

Your authentication system is now fully functional with a beautiful UI!

**Go to: http://localhost:5001/login and start exploring!**
