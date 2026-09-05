/**
 * GENESIS SOVEREIGN CORE v8.0
 * Architecture:
 * 1. WebCrypto SHA-256 Client-Side Private Workspace Authentication & Session Vault
 * 2. Global Open-Source R&D Grant & Fellowship Backing (Zero Begging, 100% Free Public Good)
 *    - Allows patrons anywhere in the world to sponsor R&D / computational infrastructure
 *    - Real-time custom amount calculation (Dynamic UPI for India + Global Wire / Crypto for International)
 *    - Clean, dignified, institutional UI matching Stripe, GitHub Sponsors, or Linux Foundation
 * 3. 100% Client-Side In-Browser Execution. All utilities remain 100% free and open.
 */

(function(window) {
    'use strict';

    const CONFIG = {
        vpa: "keshavthakur07@ptyes",
        payee: "Keshav",
        currency: "INR",
        defaultGrant: "250.00",
        solanaWallet: "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
        ethWallet: "0x71C839556cb32691B72140633005D5514Fe16381",
        githubUrl: "https://github.com/keshavs40344/ai-world-core"
    };

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
            // All tools are completely free public goods
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
                            <span class="text-white font-bold hidden sm:inline max-w-[120px] truncate">${user.displayName || user.email.split('@')[0]}</span>
                            <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                            <button onclick="GenesisAuth.logout()" title="Logout" class="text-slate-500 hover:text-rose-400 text-xs ml-1 transition">✕</button>
                        </div>
                        <button onclick="GenesisDonation.open()" class="hidden sm:inline-flex items-center gap-1.5 text-xs font-semibold text-cyan-300 hover:text-white px-3 py-1.5 rounded-xl border border-cyan-500/30 bg-cyan-500/10 hover:bg-cyan-500/20 transition font-mono">
                            <span>⚡</span>
                            <span>Back R&amp;D</span>
                        </button>
                    </div>
                `;
            } else {
                authContainer.innerHTML = `
                    <div class="flex items-center gap-2">
                        <button onclick="GenesisAuth.openModal('login')" class="text-xs font-semibold text-slate-200 hover:text-white px-3.5 py-1.5 rounded-xl border border-slate-700 hover:border-slate-500 bg-slate-900/80 transition font-sans">
                            Sign In
                        </button>
                        <button onclick="GenesisDonation.open()" class="inline-flex items-center gap-1.5 text-xs font-semibold text-cyan-300 hover:text-white px-3 py-1.5 rounded-xl border border-cyan-500/30 bg-cyan-500/10 hover:bg-cyan-500/20 transition font-mono">
                            <span>⚡</span>
                            <span>Back R&amp;D</span>
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

                    <!-- OAuth Providers (GitHub & Google via Firebase) -->
                    <div class="space-y-2.5 mb-4">
                        <!-- Sign in with GitHub -->
                        <button id="btnGitHubSignInModal" type="button" onclick="window.handleFirebaseGitHubSignIn()" class="w-full py-2.5 px-4 rounded-xl bg-slate-950 hover:bg-slate-800 border border-slate-700 hover:border-slate-500 text-white text-xs font-mono font-bold flex items-center justify-center gap-2.5 transition shadow-sm group">
                            <svg class="w-4 h-4 fill-white group-hover:scale-105 transition-transform" viewBox="0 0 24 24">
                                <path fill-rule="evenodd" clip-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"/>
                            </svg>
                            <span>Sign in with GitHub</span>
                        </button>

                        <!-- Sign in with Google -->
                        <button id="btnGoogleSignInModal" type="button" onclick="window.handleFirebaseGoogleSignIn()" class="w-full py-2.5 px-4 rounded-xl bg-slate-950 hover:bg-slate-800 border border-slate-700 hover:border-slate-500 text-white text-xs font-mono font-bold flex items-center justify-center gap-2.5 transition shadow-sm">
                            <svg class="w-4 h-4" viewBox="0 0 24 24">
                                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/>
                                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/>
                            </svg>
                            <span>Sign in with Google</span>
                        </button>
                    </div>

                    <div class="relative my-3 text-center">
                        <div class="absolute inset-0 flex items-center"><div class="w-full border-t border-slate-800"></div></div>
                        <span class="relative px-3 bg-slate-900 text-[10px] font-mono text-slate-500">OR WITH EMAIL</span>
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

            window.handleFirebaseGitHubSignIn = async function() {
        if (window.GenesisFirebase) {
            const res = await window.GenesisFirebase.signInWithGitHub();
            if (res.success) {
                if (window.GenesisAuth) window.GenesisAuth.closeModal();
                alert(`Welcome @${res.user.displayName}! Successfully authenticated with GitHub via Firebase.`);
                if (window.location.pathname.endsWith("login.html")) {
                    window.location.href = "index.html";
                }
            } else if (res.msg) {
                alert(res.msg);
            }
        } else {
            alert("Firebase client bridge loading... Please try again.");
        }
    };

    window.handleFirebaseGoogleSignIn = async function() {
        if (window.GenesisFirebase) {
            const res = await window.GenesisFirebase.signInWithGoogle();
            if (res.success) {
                if (window.GenesisAuth) window.GenesisAuth.closeModal();
                alert(`Welcome ${res.user.displayName}! Signed in securely with Google Firebase.`);
            } else if (res.msg) {
                alert(res.msg);
            }
        } else {
            alert("Firebase client bridge loading... Please try again.");
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

    // ==========================================
    // 3. GLOBAL R&D GRANT & FELLOWSHIP ENGINE
    //    (Enterprise Institutional Backing, Zero Begging)
    // ==========================================
    const GenesisDonation = {
        currentAmount: CONFIG.defaultGrant,
        activeTab: "domestic", // "domestic" (UPI) or "international" (Crypto/Wire)

        open: function(opts = {}) {
            let amount = opts.amount || this.currentAmount || CONFIG.defaultGrant;
            this._renderModal(amount);
        },

        close: function() {
            const modal = document.getElementById("genesisDonationModal");
            if (modal) modal.classList.add("hidden");
        },

        switchTab: function(tab) {
            this.activeTab = tab;
            const domView = document.getElementById("grantDomesticView");
            const intView = document.getElementById("grantInternationalView");
            const btnDom = document.getElementById("tabBtnDomestic");
            const btnInt = document.getElementById("tabBtnInternational");

            if (!domView) return;

            if (tab === "domestic") {
                domView.classList.remove("hidden");
                intView.classList.add("hidden");
                btnDom.className = "flex-1 py-2 text-xs font-mono font-bold text-white border-b-2 border-cyan-400 transition";
                btnInt.className = "flex-1 py-2 text-xs font-mono font-medium text-slate-400 hover:text-white transition";
            } else {
                domView.classList.add("hidden");
                intView.classList.remove("hidden");
                btnDom.className = "flex-1 py-2 text-xs font-mono font-medium text-slate-400 hover:text-white transition";
                btnInt.className = "flex-1 py-2 text-xs font-mono font-bold text-white border-b-2 border-cyan-400 transition";
            }
        },

        updateAmount: function(val) {
            let num = parseFloat(val);
            if (isNaN(num) || num <= 0) {
                num = 250.00;
            }
            this.currentAmount = num.toFixed(2);
            this._refreshDynamicUpi();
        },

        _refreshDynamicUpi: function() {
            const amount = this.currentAmount;
            const upiParams = new URLSearchParams({
                pa: CONFIG.vpa,
                pn: CONFIG.payee,
                am: amount,
                cu: "INR",
                tn: "Genesis_OpenSource_RD_Grant"
            });
            const genericUpi = `upi://pay?${upiParams.toString()}`;
            const gpayUri = `tez://upi/pay?${upiParams.toString()}`;
            const phonepeUri = `phonepe://pay?${upiParams.toString()}`;
            const paytmUri = `paytmmp://pay?${upiParams.toString()}`;
            const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=160x160&data=${encodeURIComponent(genericUpi)}`;

            const display = document.getElementById("grantAmountDisplay");
            const qrImg = document.getElementById("grantQrImg");
            const input = document.getElementById("grantCustomInput");
            const btnGeneric = document.getElementById("grantGenericBtn");
            const btnPhonepe = document.getElementById("grantPhonepeBtn");
            const btnGpay = document.getElementById("grantGpayBtn");
            const btnPaytm = document.getElementById("grantPaytmBtn");

            if (display) display.innerText = `₹${amount}`;
            if (input && input.value !== amount) input.value = amount;
            if (qrImg) qrImg.src = qrUrl;
            if (btnGeneric) btnGeneric.href = genericUpi;
            if (btnPhonepe) btnPhonepe.href = phonepeUri;
            if (btnGpay) btnGpay.href = gpayUri;
            if (btnPaytm) btnPaytm.href = paytmUri;
        },

        _renderModal: function(amount) {
            this.currentAmount = amount;
            let modal = document.getElementById("genesisDonationModal");
            if (!modal) {
                this._injectDonationModal();
                modal = document.getElementById("genesisDonationModal");
            }
            this._refreshDynamicUpi();
            this.switchTab(this.activeTab);
            modal.classList.remove("hidden");
        },

        _injectDonationModal: function() {
            const div = document.createElement("div");
            div.id = "genesisDonationModal";
            div.className = "fixed inset-0 bg-black/85 backdrop-blur-md z-50 hidden flex items-center justify-center p-4 font-sans antialiased";
            div.innerHTML = `
                <div class="bg-slate-900 border border-slate-800 max-w-lg w-full rounded-3xl p-6 sm:p-7 shadow-2xl relative text-slate-100 max-h-[94vh] overflow-y-auto">
                    <button onclick="GenesisDonation.close()" class="absolute top-5 right-5 text-slate-400 hover:text-white text-base font-bold">✕</button>
                    
                    <!-- Institutional Header -->
                    <div class="text-center pb-2">
                        <div class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[11px] font-mono font-semibold bg-cyan-950/80 text-cyan-300 border border-cyan-800/80 mb-3">
                            <span>●</span>
                            <span>OPEN RESEARCH &amp; INFRASTRUCTURE SPONSORSHIP</span>
                        </div>
                        <h3 class="text-xl font-display font-extrabold text-white">Back Autonomous R&amp;D</h3>
                        <p class="text-xs text-slate-400 mt-1.5 leading-relaxed max-w-md mx-auto">
                            All 49+ developer utilities and SaaS studios remain <strong class="text-white">100% free, private, and open for everyone</strong>. If these systems deliver value to your engineering workflows, you may voluntarily sponsor our compute, zero-cost architecture, and independent open-source research.
                        </p>
                    </div>

                    <!-- Method Tabs (Domestic UPI / Global Backers) -->
                    <div class="flex border-b border-slate-800 my-4 text-center">
                        <button id="tabBtnDomestic" onclick="GenesisDonation.switchTab('domestic')" class="flex-1 py-2 text-xs font-mono font-bold text-white border-b-2 border-cyan-400 transition">
                            UPI / India (Dynamic Amount)
                        </button>
                        <button id="tabBtnInternational" onclick="GenesisDonation.switchTab('international')" class="flex-1 py-2 text-xs font-mono font-medium text-slate-400 hover:text-white transition">
                            Global / Crypto Backers
                        </button>
                    </div>

                    <!-- TAB 1: DOMESTIC UPI WITH REAL-TIME AMOUNT SYNC -->
                    <div id="grantDomesticView" class="space-y-4">
                        <!-- Custom Amount Controller -->
                        <div>
                            <div class="flex justify-between items-center text-xs font-mono text-slate-400 mb-1.5">
                                <span>Enter Any Contribution Amount:</span>
                                <span class="text-cyan-400 font-bold">Auto-Syncs with QR Code</span>
                            </div>
                            <div class="relative">
                                <span class="absolute left-3.5 top-1/2 -translate-y-1/2 font-mono font-bold text-slate-400 text-sm">₹</span>
                                <input 
                                    id="grantCustomInput"
                                    type="number"
                                    min="1"
                                    step="1"
                                    value="${CONFIG.defaultGrant}"
                                    class="w-full bg-slate-950 border border-slate-800 focus:border-cyan-500 rounded-xl pl-8 pr-4 py-2.5 text-sm font-mono text-white focus:outline-none transition"
                                    placeholder="Enter custom amount"
                                    oninput="GenesisDonation.updateAmount(this.value)"
                                />
                            </div>
                        </div>

                        <!-- Dynamic QR Display Container -->
                        <div class="bg-slate-950/90 border border-slate-800 rounded-2xl p-4 text-center">
                            <div class="flex justify-between items-center text-xs font-mono text-slate-400 mb-2">
                                <span>Target Contribution:</span>
                                <span id="grantAmountDisplay" class="text-cyan-400 font-mono font-bold text-base">₹${CONFIG.defaultGrant}</span>
                            </div>
                            <div class="bg-white p-2.5 rounded-xl inline-block shadow-inner mx-auto mb-2 border-2 border-cyan-500/20">
                                <img id="grantQrImg" src="" alt="Dynamic Contribution QR" class="w-36 h-36 mx-auto block"/>
                            </div>
                            <p class="text-[11px] text-slate-400 font-mono select-all font-semibold text-cyan-300">${CONFIG.vpa}</p>
                            <button onclick="navigator.clipboard.writeText('${CONFIG.vpa}'); alert('UPI ID copied: ${CONFIG.vpa}')" class="text-[11px] text-indigo-400 hover:underline mt-1 block mx-auto font-mono">
                                📋 Copy Direct UPI ID
                            </button>
                        </div>

                        <!-- Direct App Launchers -->
                        <div class="space-y-2">
                            <span class="text-[11px] font-mono text-slate-400 uppercase tracking-wider block">One-Tap Direct Launch:</span>
                            <div class="grid grid-cols-3 gap-2">
                                <a id="grantPhonepeBtn" href="#" class="bg-purple-950/80 border border-purple-800/80 hover:bg-purple-900 text-purple-200 text-xs font-bold py-2.5 text-center rounded-xl transition font-mono">
                                    PhonePe
                                </a>
                                <a id="grantGpayBtn" href="#" class="bg-blue-950/80 border border-blue-800/80 hover:bg-blue-900 text-blue-200 text-xs font-bold py-2.5 text-center rounded-xl transition font-mono">
                                    GPay
                                </a>
                                <a id="grantPaytmBtn" href="#" class="bg-sky-950/80 border border-sky-800/80 hover:bg-sky-900 text-sky-200 text-xs font-bold py-2.5 text-center rounded-xl transition font-mono">
                                    Paytm
                                </a>
                            </div>
                            <a id="grantGenericBtn" href="#" class="w-full bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-bold text-xs py-3 rounded-xl block text-center transition font-mono shadow-lg shadow-cyan-900/30">
                                ⚡ Open Default UPI App
                            </a>
                        </div>
                    </div>

                    <!-- TAB 2: GLOBAL / CRYPTO / WIRE FOR BACKERS ANYWHERE IN THE WORLD -->
                    <div id="grantInternationalView" class="hidden space-y-4">
                        <div class="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
                            <h4 class="text-xs font-mono font-bold text-white flex items-center gap-1.5">
                                <span>🌐</span> Global Backers &amp; Grants
                            </h4>
                            <p class="text-[11px] text-slate-400 leading-relaxed font-mono">
                                For supporters outside India, you can sponsor computing infrastructure via native cryptographic settlement or GitHub Sponsors.
                            </p>
                        </div>

                        <!-- Solana Network -->
                        <div class="p-3 bg-slate-950 border border-slate-800 rounded-xl space-y-1 text-xs font-mono">
                            <div class="flex justify-between items-center">
                                <span class="text-purple-400 font-bold">Solana (SOL / USDC)</span>
                                <button onclick="navigator.clipboard.writeText('${CONFIG.solanaWallet}'); alert('Solana address copied!')" class="text-indigo-400 hover:underline text-[10px]">Copy</button>
                            </div>
                            <p class="text-slate-300 text-[10px] break-all select-all">${CONFIG.solanaWallet}</p>
                        </div>

                        <!-- Ethereum Network -->
                        <div class="p-3 bg-slate-950 border border-slate-800 rounded-xl space-y-1 text-xs font-mono">
                            <div class="flex justify-between items-center">
                                <span class="text-blue-400 font-bold">Ethereum (ETH / USDT)</span>
                                <button onclick="navigator.clipboard.writeText('${CONFIG.ethWallet}'); alert('Ethereum address copied!')" class="text-indigo-400 hover:underline text-[10px]">Copy</button>
                            </div>
                            <p class="text-slate-300 text-[10px] break-all select-all">${CONFIG.ethWallet}</p>
                        </div>

                        <!-- GitHub Sponsors Link -->
                        <a href="${CONFIG.githubUrl}" target="_blank" class="w-full py-3 rounded-xl border border-slate-700 hover:border-slate-500 bg-slate-800/80 hover:bg-slate-800 text-white font-mono text-xs font-bold block text-center transition flex items-center justify-center gap-2">
                            <span>⭐ Star &amp; Sponsor on GitHub</span>
                        </a>
                    </div>

                    <!-- Footer Microcopy -->
                    <div class="mt-5 pt-3 border-t border-slate-800 text-center">
                        <p class="text-[10px] font-mono text-slate-500">
                            100% Free Public Software • Zero Compulsion • Pure Open-Source Research
                        </p>
                    </div>
                </div>
            `;
            document.body.appendChild(div);
        }
    };

    // Stubs for backwards compatibility
    const GenesisSupport = GenesisDonation;
    const GenesisCheckout = {
        open: function() { GenesisDonation.open(); },
        close: function() { GenesisDonation.close(); }
    };

    // Auto-mount on DOM ready
    window.addEventListener("DOMContentLoaded", () => {
        GenesisAuth.updateNavbarAuth();
    });

    window.GenesisAuth = GenesisAuth;
    window.GenesisDonation = GenesisDonation;
    window.GenesisSupport = GenesisSupport;
    window.GenesisCheckout = GenesisCheckout;

})(window);
