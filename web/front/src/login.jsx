import './login.css'

function LogIn() {
  return (
    <>
    <div class="wrapper">
      <form action="#">
        <h2>Login</h2>
        <div class="input-field">
          <input type="text" required></input>
          <label>Enter your username</label>
        </div>
        <div class="input-field">
          <input type="password" required></input>
          <label>Enter your password</label>
        </div>
        <div class="forget">
          <label for="remember">
            <input type="checkbox" id="remember"></input>
            <p>Remember me</p>
          </label>
          <a href="#">Forgot password?</a>
        </div>
        <button type="submit">Log In</button>
        <div class="register">
          <p>Don't have an account? <a href="#">Sign up</a></p>
        </div>
      </form>
    </div>
    </> 
    )
}

export default LogIn
