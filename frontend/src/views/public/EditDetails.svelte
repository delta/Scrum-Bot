<Nav/>
<svelte:head>
  <title>Edit Details</title>
</svelte:head>
<section class="login">
  <div class="login-container register-container">
      <h3 class="title">Edit Details</h3>
      <p class="separator"><span>&nbsp;</span></p>
      <form
        class="signup-form"
        on:submit|preventDefault="{save}"
      >
        {#if error}
          <span class="error-message">
            {error}
          </span>
        {/if}
        <div class="form-group">
            <label for="rollno">Rollno</label>
            <input
              class="text-input rollno-input"
              disabled
              bind:value="{user.rollno}"
              type="text"
              placeholder="Rollno"
              id="rollno"
              required pattern="[0-9]&#123;9&#125;"
            >
        </div>
        <div class="form-group">
          <label for="batch">Batch</label>
          <input
            class="text-input batch-input"
            bind:value="{user.batch}"
            type="text"
            placeholder="Batch (eg: 2021)"
            id="batch"
            required pattern="[0-9]&#123;4&#125;"
          >
        </div>
        <div class="form-group">
          <label for="name">Name</label>
          <input
            class="text-input name-input"
            bind:value="{user.name}"
            type="text"
            placeholder="Name"
            id="name"
            required
          >
        </div>
        <div class="form-group">
            <label for="dischandle">Discord username</label>
            <input
              class="text-input name-input"
              bind:value="{user.discordHandle}"
              type="text"
              placeholder="Discord username"
              id="dischandle"
              required
            >
        </div>
        <button
          class="signup-button"
          disabled="{inProgress}"
        >
        {#if inProgress}
          <img class="wait" src="https://i.stack.imgur.com/AfStP.gif" alt="loading..">
        {:else}
          SAVE DETAILS
        {/if}
        </button>
      </form>
  </div>
</section>
<ToastContainer placement="bottom-right" let:data={data}>
  <FlatToast {data} />
</ToastContainer>
<FootNote/>
<style src="../../css/login.scss" lang="scss"></style>
<script src='../../js/editdetails.js'></script>
