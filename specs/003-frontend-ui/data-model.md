# Data Model: Frontend UI & UX for Todo Application

## Entity: Todo Item

**Fields**:
- id: string (unique identifier)
- title: string (required, maximum 255 characters)
- description: string | null (optional, maximum 1000 characters)
- completed: boolean (default: false)
- createdAt: Date (timestamp when created)
- updatedAt: Date (timestamp when last updated)
- userId: string (foreign key to authenticated user)

**Validation rules**:
- Title must be 1-255 characters
- Description must be 0-1000 characters if provided
- Completed must be a boolean value
- userId must match the authenticated user's ID

**State transitions**:
- New todo: {completed: false}
- Toggle completion: {completed: !completed}
- Update: {updatedAt: current_timestamp}

## Entity: User Session

**Fields**:
- userId: string (authenticated user ID from JWT)
- jwtToken: string (JWT token for API authentication)
- expiresAt: Date (token expiration timestamp)
- isAuthenticated: boolean (session status)

**Validation rules**:
- JWT token must be valid and not expired
- userId must exist in the system
- Token must include proper audience and issuer claims

**State transitions**:
- Login: {isAuthenticated: true, jwtToken: [new_token]}
- Logout: {isAuthenticated: false, jwtToken: null}
- Token refresh: {jwtToken: [refreshed_token], expiresAt: [new_expiry]}

## Entity: UI State

**Fields**:
- loading: boolean (indicates ongoing API requests)
- error: string | null (error messages for user feedback)
- success: string | null (success messages for user feedback)
- currentView: string (current page/route)
- breakpoints: object (responsive design state)

**Validation rules**:
- Only one of error or success should be active at a time
- Loading state should be tied to specific API operations
- Breakpoints should reflect actual screen size

**State transitions**:
- API start: {loading: true}
- API success: {loading: false, success: [message]}
- API error: {loading: false, error: [message]}
- Navigation: {currentView: [new_view]}

## Entity: Form State

**Fields**:
- formData: object (form input values)
- touched: object (which fields have been interacted with)
- errors: object (validation errors per field)
- isValid: boolean (overall form validity)

**Validation rules**:
- Form data must match expected schema
- Errors should be cleared when field values change
- Touched state should only change on user interaction

**State transitions**:
- Field change: {formData[field]: value, errors[field]: validate(value)}
- Submit attempt: {touched: all_fields, errors: validate_all()}
- Reset: {formData: initial_values, errors: {}, touched: {}}