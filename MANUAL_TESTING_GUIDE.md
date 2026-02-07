# Manual Testing Guide - Phase III Todo Application

## Prerequisites
- ✅ Backend server running on http://localhost:8000
- ✅ Frontend server running on http://localhost:3000
- ✅ Backend API verified and working

## Test Checklist

### 1. Signup Flow Testing

**Steps:**
1. Open http://localhost:3000 in your browser
2. Navigate to the signup page (look for "Sign Up" or "Register" link)
3. Fill in the signup form:
   - Email: `test@example.com`
   - Password: `Test1234!` (must meet requirements: 8+ chars, uppercase, lowercase, number)
4. Click the signup/register button

**Expected Results:**
- ✅ Form validates password requirements
- ✅ User account is created
- ✅ User is automatically logged in
- ✅ Redirected to tasks/dashboard page
- ✅ JWT token is stored in browser (check localStorage/cookies in DevTools)

**Possible Issues:**
- ❌ Email already exists error → Use a different email
- ❌ Password validation error → Check password meets all requirements
- ❌ Network error → Check backend is running on port 8000

---

### 2. Login Flow Testing

**Steps:**
1. If already logged in, log out first
2. Navigate to the login page
3. Fill in the login form:
   - Email: Use the email from signup test
   - Password: Use the password from signup test
4. Click the login button

**Expected Results:**
- ✅ User is authenticated
- ✅ Redirected to tasks/dashboard page
- ✅ JWT token is stored
- ✅ User can see their tasks (if any exist)

**Possible Issues:**
- ❌ Invalid credentials error → Check email/password are correct
- ❌ Network error → Check backend is running

---

### 3. Task Creation Testing

**Steps:**
1. Ensure you're logged in
2. Navigate to the tasks page (should be automatic after login)
3. Look for "Add Task" or "Create Task" button/form
4. Enter a task title: `Buy groceries`
5. Submit the form

**Expected Results:**
- ✅ Task appears in the task list immediately
- ✅ Task shows as incomplete/not done
- ✅ Task has the correct title
- ✅ No page refresh required (should update dynamically)

**Test Multiple Tasks:**
- Create 3-5 more tasks with different titles
- Verify all tasks appear in the list

---

### 4. Task Viewing Testing

**Steps:**
1. View the list of all your tasks
2. Check the task details displayed

**Expected Results:**
- ✅ All tasks are visible
- ✅ Each task shows: title, completion status
- ✅ Tasks are sorted (typically by creation date)
- ✅ Only YOUR tasks are visible (not other users' tasks)

**Optional:**
- Click on a task to view details (if individual task page exists)
- Verify task details are correct

---

### 5. Task Editing Testing

**Steps:**
1. Find a task in your list
2. Look for an "Edit" button or click on the task
3. Change the task title to something new
4. Save the changes

**Expected Results:**
- ✅ Task title updates in the list
- ✅ Changes persist (refresh page to verify)
- ✅ No errors occur

---

### 6. Task Completion Toggle Testing

**Steps:**
1. Find an incomplete task
2. Click the checkbox or "Mark Complete" button
3. Observe the task status change

**Expected Results:**
- ✅ Task is marked as complete
- ✅ Visual indication of completion (checkmark, strikethrough, color change)
- ✅ Can toggle back to incomplete
- ✅ Changes persist after page refresh

**Test:**
- Toggle several tasks between complete/incomplete
- Refresh the page and verify states are saved

---

### 7. Task Deletion Testing

**Steps:**
1. Find a task you want to delete
2. Click the "Delete" or trash icon button
3. Confirm deletion (if confirmation dialog appears)

**Expected Results:**
- ✅ Task is removed from the list immediately
- ✅ Task does not reappear after page refresh
- ✅ No errors occur

**Test:**
- Delete multiple tasks
- Verify count updates correctly

---

### 8. Responsive Design Testing

**Steps:**
1. Open browser DevTools (F12)
2. Toggle device toolbar (Ctrl+Shift+M or Cmd+Shift+M)
3. Test different screen sizes:
   - Mobile: 375px width (iPhone)
   - Tablet: 768px width (iPad)
   - Desktop: 1920px width

**Expected Results:**
- ✅ Layout adapts to screen size
- ✅ All buttons are clickable on mobile
- ✅ Text is readable on all sizes
- ✅ No horizontal scrolling on mobile
- ✅ Forms are usable on touch devices

---

### 9. Error Handling Testing

**Test Invalid Login:**
1. Try to log in with wrong password
2. Expected: Clear error message displayed

**Test Network Error:**
1. Stop the backend server
2. Try to create a task
3. Expected: Error message about connection failure
4. Restart backend and verify recovery

**Test Session Expiration:**
1. Log in and get a token
2. Wait for token to expire (or manually clear it from DevTools)
3. Try to perform an action
4. Expected: Redirected to login page

---

### 10. Complete User Journey Testing

**Full Flow:**
1. Start at home page
2. Sign up with new account
3. Create 5 tasks
4. Mark 2 tasks as complete
5. Edit 1 task title
6. Delete 1 task
7. Log out
8. Log back in
9. Verify all tasks are still there with correct states

**Expected Results:**
- ✅ Entire flow works smoothly
- ✅ Data persists across login sessions
- ✅ No errors or broken functionality

---

## Browser Console Checks

Open DevTools Console (F12) and check for:
- ❌ No JavaScript errors (red messages)
- ❌ No failed network requests (check Network tab)
- ✅ API calls return 200/201 status codes
- ✅ JWT token is included in request headers

## Performance Checks

- ✅ Pages load in under 3 seconds
- ✅ Task operations feel instant (no lag)
- ✅ Smooth animations and transitions

## Accessibility Checks

- ✅ Can navigate with keyboard (Tab key)
- ✅ Forms have proper labels
- ✅ Buttons have clear text/icons
- ✅ Color contrast is readable

---

## Reporting Issues

If you find any issues, note:
1. What you were trying to do
2. What happened (error message, unexpected behavior)
3. Browser console errors (if any)
4. Network request details (from DevTools Network tab)

---

## Success Criteria

All tests pass = ✅ **Frontend is production-ready**

Any failures = ⚠️ **Issues need to be fixed**
