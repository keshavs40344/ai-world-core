/**
 * GENESIS SOVEREIGN AUTHENTICATION & WORKSPACE CORE v7.0
 * Pure Enterprise Identity & Client-Side Workspace Memory.
 * 100% Free, Private & Open Software.
 * ZERO DONATIONS • ZERO PAYWALLS • ZERO FINANCIAL MODALS
 */

(function(window) {
    'use strict';

    // ==========================================
    // 1. WEBCRYPTO SHA-256 HASHING
    // ==========================================
    async function sha256(str) {
        try {
            const buf = new TextEncoder().encode(str + "_genesis_sovereign_salt_2026");
            const hashBuf = await crypto.subtle.digest("SHA-256", buf);
            const hashArr = Array.from(new Uint8Array(hashBuf));
            return hashArr.map(b => b.toString(16).padStart(2, '0')).join('');
        } catch(e) {
            let hash = 0;
            for (let i = 0; i < str.length; i++) {
                hash = ((hash << 5) - hash) + str.charCodeAt(i);
                hash |= 0;
            }
            return "h_" + Math.abs(hash).toString(16);
        }
    }

    // ==========================================
    // 2. SOVEREIGN AUTH ENGINE (Local Vault)
    // ==========================================
    const GenesisAuth = {
        getUserVault: function() {
            try {
                const vault = localStorage.getItem("genesis_users_vault");
                return vault ? JSON.parse(vault) : {};
            } catch(e) {
                return {};
            }
        },

        getCurrentUser: function() {
            try {
                const user = localStorage.getItem("genesis_current_user");
                return user ? JSON.parse(user) : null;
            } catch(e) {
                return null;
            }
        },

        isLoggedIn: function() {
            return this.getCurrentUser() !== null;
        },

        hasProAccess: function() {
            // All tools are completely free and unrestricted
            return true;
        },

        register: async function(email, password, displayName) {
            const cleanEmail = email ? email.trim().toLowerCase() : "";
            if (!cleanEmail || !cleanEmail.includes("@")) {
                return { success: false, msg: "Valid email address is required." };
            }
            if (!password || password.length < 4) {
                return { success: false, msg: "Password must be at least 4 characters long." };
            }

            const vault = this.getUserVault();
            if (vault[cleanEmail]) {
                return { success: false, msg: "An account with this email already exists. Please Sign In." };
            }

            const passHash = await sha256(password);
            const name = displayName && displayName.trim() ? displayName.trim() : cleanEmail.split("@")[0];
            const newUser = {
                email: cleanEmail,
                displayName: name,
                passHash: passHash,
                avatar: name.charAt(0).toUpperCase(),
                createdAt: new Date().toISOString()
            };

            vault[cleanEmail] = newUser;
            localStorage.setItem("genesis_users_vault", JSON.stringify(vault));

            const sessionUser = {
                email: newUser.email,
                displayName: newUser.displayName,
                avatar: newUser.avatar,
                token: "gnx_" + Math.random().toString(36).substr(2, 12),
                loginAt: new Date().toISOString()
            };
            localStorage.setItem("genesis_current_user", JSON.stringify(sessionUser));
            this.updateNavbarAuth();
            return { success: true, user: sessionUser };
        },

        login: async function(email, password) {
            const cleanEmail = email ? email.trim().toLowerCase() : "";
            if (!cleanEmail || !password) {
                return { success: false, msg: "Email and password are required." };
            }

            const vault = this.getUserVault();
            const user = vault[cleanEmail];
            const passHash = await sha256(password);

            if (!user) {
                return this.register(cleanEmail, password);
            }

            if (user.passHash !== passHash) {
                return { success: false, msg: "Incorrect password. Please try again." };
            }

            const sessionUser = {
                email: user.email,
                displayName: user.displayName,
                avatar: user.avatar,
                token: "gnx_" + Math.random().toString(36).substr(2, 12),
                loginAt: new Date().toISOString()
            };
            localStorage.setItem("genesis_current_user", JSON.stringify(sessionUser));
            this.updateNavbarAuth();
            return { success: true, user: sessionUser };
        },

        loginAsGuest: function() {
            const guestId = Math.floor(1000 + Math.random() * 9000);
            const guestUser = {
                email: `guest_${guestId}@genesis.world`,
                displayName: `Guest #${guestId}`,
                avatar: "G",
                token: "gnx_guest_" + guestId,
                loginAt: new Date().toISOString(),
                isGuest: true
            };
            localStorage.setItem("genesis_current_user", JSON.stringify(guestUser));
            this.updateNavbarAuth();
            return { success: true, user: guestUser };
        },

        logout: function() {
            localStorage.removeItem("genesis_current_user");
            this.updateNavbarAuth();
            window.location.reload();
        },

        updateNavbarAuth: function() {
            const authContainer = document.getElementById("genesisAuthWidget");
            if (!authContainer) return;

            const user = this.getCurrentUser();
            if (user) {
                authContainer.innerHTML = `
                    <div class="flex items-center gap-2">
                        <div class="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs font-mono">
                            <span class="w-5 h-5 rounded-full bg-emerald-500 text-slate-950 font-black flex items-center justify-center text-[10px]">
                                ${user.avatar || 'Ω'}
                            </span>
                            <span class="text-white font-bold hidden sm:inline max-w-[130px] truncate">${user.displayName || user.email.split('@')[0]}</span>
                            <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                            <button onclick="GenesisAuth.logout()" title="Logout" class="text-slate-500 hover:text-rose-400 text-xs ml-1 transition">✕</button>
                        </div>
                    </div>
                `;
            } else {
                authContainer.innerHTML = `
                    <div class="flex items-center gap-2">
                        <button onclick="GenesisAuth.openModal('login')" class="text-xs font-semibold text-slate-200 hover:text-white px-3.5 py-1.5 rounded-xl border border-slate-700 hover:border-slate-500 bg-slate-900/80 transition">
                            Sign In / Account
                        </button>
                    </div>
                `;
            }
        },

        openModal: function(mode = 'login') {
            let modal = document.getElementById("genesisAuthModal");
            if (!modal) {
                this._injectAuthModal();
                modal = document.getElementById("genesisAuthModal");
            }
            this.switchModalTab(mode);
            modal.classList.remove("hidden");
        },

        closeModal: function() {
            const modal = document.getElementById("genesisAuthModal");
            if (modal) modal.classList.add("hidden");
        },

        switchModalTab: function(mode) {
            const isLogin = mode === 'login';
            const tabLogin = document.getElementById("authTabLogin");
            const tabRegister = document.getElementById("authTabRegister");
            const nameField = document.getElementById("authNameContainer");
            const submitBtn = document.getElementById("authSubmitBtn");
            const modalTitle = document.getElementById("authModalTitle");
            const togglePrompt = document.getElementById("authTogglePrompt");

            if (!tabLogin) return;

            if (isLogin) {
                tabLogin.className = "flex-1 py-2 text-xs font-bold text-white border-b-2 border-emerald-500 transition";
                tabRegister.className = "flex-1 py-2 text-xs font-medium text-slate-400 hover:text-white transition";
                nameField.classList.add("hidden");
                submitBtn.innerText = "Sign In to Workspace";
                modalTitle.innerText = "Welcome Back";
                togglePrompt.innerHTML = `Don't have an account? <button onclick="GenesisAuth.switchModalTab('register')" class="text-emerald-400 hover:underline font-bold">Create one free</button>`;
                document.getElementById("authForm").setAttribute("data-mode", "login");
            } else {
                tabLogin.className = "flex-1 py-2 text-xs font-medium text-slate-400 hover:text-white transition";
                tabRegister.className = "flex-1 py-2 text-xs font-bold text-white border-b-2 border-emerald-500 transition";
                nameField.classList.remove("hidden");
                submitBtn.innerText = "Create Free Account";
                modalTitle.innerText = "Create Sovereign Account";
                togglePrompt.innerHTML = `Already have an account? <button onclick="GenesisAuth.switchModalTab('login')" class="text-emerald-400 hover:underline font-bold">Sign In</button>`;
                document.getElementById("authForm").setAttribute("data-mode", "register");
            }
        },

        _injectAuthModal: function() {
            const div = document.createElement("div");
            div.id = "genesisAuthModal";
            div.className = "fixed inset-0 bg-black/85 backdrop-blur-md z-50 hidden flex items-center justify-center p-4 font-sans antialiased";
            div.innerHTML = `
                <div class="bg-slate-900 border border-slate-800 max-w-md w-full rounded-3xl p-6 sm:p-7 shadow-2xl relative text-slate-100">
                    <button onclick="GenesisAuth.closeModal()" class="absolute top-5 right-5 text-slate-400 hover:text-white text-base font-bold">✕</button>
                    
                    <div class="text-center pb-2">
                        <div class="w-12 h-12 rounded-2xl bg-gradient-to-tr from-emerald-500 to-teal-500 flex items-center justify-center text-xl font-black text-slate-950 mx-auto mb-3 shadow-lg shadow-emerald-500/25">
                            Ω
                        </div>
                        <h3 id="authModalTitle" class="text-xl font-extrabold text-white">Welcome Back</h3>
                        <p class="text-xs text-slate-400 mt-1">100% Private Client-Side Workspace Authentication</p>
                    </div>

                    <!-- Mode Selector Tabs -->
                    <div class="flex border-b border-slate-800 my-4 text-center">
                        <button id="authTabLogin" onclick="GenesisAuth.switchModalTab('login')" class="flex-1 py-2 text-xs font-bold text-white border-b-2 border-emerald-500 transition">Sign In</button>
                        <button id="authTabRegister" onclick="GenesisAuth.switchModalTab('register')" class="flex-1 py-2 text-xs font-medium text-slate-400 hover:text-white transition">Register Free</button>
                    </div>

                    <!-- Interactive Form -->
                    <form id="authForm" data-mode="login" onsubmit="event.preventDefault(); window.handleSovereignAuth();" class="space-y-3.5">
                        <div id="authNameContainer" class="hidden">
                            <label class="text-[11px] font-mono text-slate-400 uppercase">Your Name</label>
                            <input id="authNameInput" type="text" placeholder="e.g. Keshav Sharma" class="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-white mt-1 focus:outline-none focus:border-emerald-500 font-mono">
                        </div>
                        <div>
                            <label class="text-[11px] font-mono text-slate-400 uppercase">Email Address</label>
                            <input id="authEmailInput" type="email" required placeholder="you@domain.com" class="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-white mt-1 focus:outline-none focus:border-emerald-500 font-mono">
                        </div>
                        <div>
                            <label class="text-[11px] font-mono text-slate-400 uppercase">Password</label>
                            <input id="authPassInput" type="password" required placeholder="••••••••••••" class="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs text-white mt-1 focus:outline-none focus:border-emerald-500 font-mono">
                        </div>
                        <button id="authSubmitBtn" type="submit" class="w-full bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-slate-950 font-extrabold text-xs py-3.5 rounded-xl transition shadow-lg shadow-emerald-500/25 mt-2">
                            Sign In to Workspace
                        </button>
                    </form>

                    <div class="relative my-4 text-center">
                        <div class="absolute inset-0 flex items-center"><div class="w-full border-t border-slate-800"></div></div>
                        <span class="relative px-3 bg-slate-900 text-[11px] font-mono text-slate-500">OR</span>
                    </div>

                    <button onclick="GenesisAuth.loginAsGuest(); GenesisAuth.closeModal();" class="w-full py-2.5 rounded-xl border border-slate-800 hover:bg-slate-800/60 text-slate-300 text-xs font-mono transition">
                        ⚡ Continue as Instant Guest
                    </button>

                    <p id="authTogglePrompt" class="text-xs text-center text-slate-400 mt-4">
                        Don't have an account? <button onclick="GenesisAuth.switchModalTab('register')" class="text-emerald-400 hover:underline font-bold">Create one free</button>
                    </p>

                    <p class="text-[10px] text-slate-500 text-center mt-3 font-mono">
                        🔒 Zero-Server Auth. Passwords hashed locally via SHA-256 WebCrypto.
                    </p>
                </div>
            `;
            document.body.appendChild(div);
        }
    };

    window.handleSovereignAuth = async function() {
        const mode = document.getElementById("authForm").getAttribute("data-mode");
        const email = document.getElementById("authEmailInput").value;
        const pass = document.getElementById("authPassInput").value;
        const name = document.getElementById("authNameInput").value;

        if (mode === "register") {
            const res = await GenesisAuth.register(email, pass, name);
            if (res.success) {
                GenesisAuth.closeModal();
                alert(`Account created successfully! Welcome, ${res.user.displayName}!`);
            } else {
                alert(res.msg);
            }
        } else {
            const res = await GenesisAuth.login(email, pass);
            if (res.success) {
                GenesisAuth.closeModal();
                alert(`Welcome back, ${res.user.displayName}! Workspace session restored.`);
            } else {
                alert(res.msg);
            }
        }
    };

    // Global Compatibility Stubs - completely silent with zero financial modals
    const GenesisDonation = { open: function() {}, close: function() {} };
    const GenesisSupport = { open: function() {}, close: function() {} };
    const GenesisCheckout = { open: function() {}, close: function() {} };

    // Auto-mount on DOM ready
    window.addEventListener("DOMContentLoaded", () => {
        GenesisAuth.updateNavbarAuth();
    });

    window.GenesisAuth = GenesisAuth;
    window.GenesisDonation = GenesisDonation;
    window.GenesisSupport = GenesisSupport;
    window.GenesisCheckout = GenesisCheckout;

})(window);
