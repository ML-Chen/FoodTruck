<!-- Screen 2: Register -->
<script>
    let username;
    let email;
    let firstName;
    let lastName;
    let password;
    let confirmPassword;
    let balance;
    let type;
    let errorMsg;

    export async function handleRegister() {
        console.log(type)
        if (password.length < 8) {
            errorMsg = 'Password must be greater 8 characters'
        } else if (password != confirmPassword) {
            errorMsg = 'Confirm password must match password'
        } else if (!email && type) {
            errorMsg = 'Cannot be employee without email. Please enter email or refresh page if you are a customer'
        }else {
            const response = await fetch('http://127.0.0.1:4000/register', {
                method: 'POST',
                mode: 'cors',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, email, firstName, lastName, password, balance , type })
            });
            const json = await response.json();
            if (json === []) {
                errorMsg = 'Error';
            } else if (json.error) {
                errorMsg = json.error;
            } else {
                console.log("Success");
            }
        }
    }


</script>

<svelte:head>
    <title>Food Truck Register</title>
</svelte:head>

<h1>Register</h1>

<form class="form" on:submit|preventDefault={handleRegister}>
    <label for="username">Username</label>
    <input type="text" id="username" name="username" bind:value={username} />
    <label for="email">Email</label>
    <input type="text" id="email" name="email" bind:value={email} />
    <label for="firstName">First Name</label>
    <input type="text" id="firstName" name="firstName" bind:value={firstName} />
    <label for="lastName">Last Name</label>
    <input type="text" id="lastName" name="lastName" bind:value={lastName} />
    <label for="password">Password</label>
    <input type="password" id="password" name="password" bind:value={password} />
    <label for="confirmPassword">Confirm Password</label>
    <input type="password" id="confirmPassword" name="confirmPassword" bind:value={confirmPassword} />
    <label for="balance">Balance</label>
    <input type="text" id="balance" name="balance" bind:value={balance} />
    <label for="notEmployee">Not Employee</label>
    <input type="radio" id="notEmployee" name="type" value=undefined bind:group={type}>
    <label for="admin">Admin</label>
    <input type="radio" id="admin" name="type" value="Admin" bind:group={type}>
    <label for="manager">Manager</label>
    <input type="radio" id="manager" name="type" value="Manager" bind:group={type}>
    <label for="staff">Staff</label>
    <input type="radio" id="staff" name="type" value="Staff" bind:group={type}>
    <button type="button">Back</button>
    <button type="submit">Register</button>
    {#if errorMsg}
        <p class="error">{errorMsg}</p>
    {/if}
</form>