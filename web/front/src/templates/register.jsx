import '../css/register.css'
import {Helmet} from 'react-helmet'
import RegisterUpl from '../js/register.js'


function Register() {
  return (
    <>
    <div class="wrapper">
      <Helmet>
        <title>Sign up | Ручей</title>
      </Helmet>
      <form action={RegisterUpl}>
        <h2>Sign up</h2>
        <div class="input-field">
          <input type="text" required name='username'></input>
          <label>Enter your username</label>
        </div>
        <div class="input-field">
          <input type="password" required name='password'></input>
          <label>Enter your password</label>
        </div>
        <button type="submit">Sign up</button>
        <div class="login">
          <p>Have an account? <a href="/login">Log in</a></p>
        </div>
      </form>
    </div>
    </>
    )
}


export default Register;