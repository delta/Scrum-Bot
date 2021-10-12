<header class="header__navbar bg-primary">
    <div class="navbar">
        <div class="mob-nav">
            <h1 class="navbar__logo">
                <a on:click="{home}" href="#/">Delta Scrumbot</a>
                <div class="menu-wrapper" on:click="{cross}">
                    <div class="menu-line line1"></div>
                    <div class="menu-line line2"></div>
                    <div class="menu-line line3"></div>
                </div>
            </h1>
        </div>
        <ul class="navbar__links desktop">
            <li><a href="/scrum">SCRUMS</a></li>
            {#if !localStorage.getItem("token")}
                <li><a href="/register">REGISTER</a></li>
            {/if}
            {#if localStorage.getItem("token")}
                <li><a href='/edit'>EDIT PROFILE</a></li>
            {/if}
            {#if localStorage.getItem("token")}
                <li><a href='#/' on:click={logout}>LOGOUT</a></li>
            {:else}
                <li><a href="/logout">LOGIN</a></li>
            {/if}
        </ul>       
        {#if disp}
            <ul class="navbar__links mobile">
                <li><a href="/scrum">SCRUMS</a></li>
                {#if !localStorage.getItem("token")}
                    <li><a href="/register">REGISTER</a></li>
                {/if}
                {#if localStorage.getItem("token")}
                    <li><a href='/edit'>EDIT PROFILE</a></li>
                {/if}
                {#if localStorage.getItem("token")}
                    <li><a href='#/' on:click={logout}>LOGOUT</a></li>
                {:else}
                    <li><a href="/logout">LOGIN</a></li>
                {/if}
            </ul>           
        {/if}   
    </div>
</header>

<script src='../../js/nav.js'></script>
<style src="../../css/nav.scss" lang="scss"></style>
