import '../css/register.css'

function Register() {
  return (
    <>
    <div class="wrapper">
      <form action="#">
        <h2>Sign up</h2>
        <div class="input-field">
          <input type="text" required></input>
          <label>Enter your username</label>
        </div>
        <div class="input-field">
          <input type="password" required></input>
          <label>Enter your password</label>
        </div>
        <button type="submit">Sign up</button>
        <div class="login">
          <p>Have an account? <a href="#">Log in</a></p>
        </div>
      </form>
    </div>
    </>
    )
}

export default Register
