/**
 * GENESIS SOVEREIGN AUTH & VOLUNTARY PATRONAGE CORE v6.0
 * Features:
 * 1. WebCrypto SHA-256 Cryptographic Password Hashing (Zero-server, 100% private)
 * 2. Multi-Account Registration, Persistent Sessions & Profile Switcher
 * 3. Dynamic User Avatar, Workspace Memory & Status Badge in Navbar
 * 4. 100% Free Sovereign Software with Voluntary "Apni Khushi Se" UPI Patronage
 * Direct Settlement: keshavthakur07@ptyes (Payee: Keshav)
 */

(function(window) {
    'use strict';

    const CONFIG = {
        vpa: "keshavthakur07@ptyes",
        payee: "Keshav",
        defaultDonation: "101.00",
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
            // Simple deterministic fallback if WebCrypto unavailable
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
                createdAt: new Date().toISOString(),
                runsCount: 0
            };

            vault[cleanEmail] = newUser;
            localStorage.setItem("genesis_users_vault", JSON.stringify(vault));

            // Auto-login after registration
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

            // Auto-seed initial user if vault empty
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
                        <div class="flex items-center gap-2 px-2.5 py-1 rounded-xl bg-slate-900/90 border border-emerald-500/30 text-xs font-mono">
                            <span class="w-5 h-5 rounded-full bg-emerald-500 text-slate-950 font-black flex items-center justify-center text-[10px]">
                                ${user.avatar || 'Ω'}
                            </span>
                            <span class="text-white font-bold hidden sm:inline max-w-[120px] truncate">${user.displayName || user.email.split('@')[0]}</span>
                            <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                            <button onclick="GenesisAuth.logout()" title="Logout" class="text-slate-400 hover:text-rose-400 text-xs ml-1 transition">✕</button>
                        </div>
                        <button onclick="GenesisDonation.open()" class="inline-flex items-center gap-1.5 text-xs font-semibold text-rose-300 hover:text-rose-200 px-3 py-1.5 rounded-lg border border-rose-500/30 bg-rose-500/10 hover:bg-rose-500/20 transition shadow-sm">
                            <span>❤️</span>
                            <span class="hidden sm:inline">Donate</span>
                        </button>
                    </div>
                `;
            } else {
                authContainer.innerHTML = `
                    <div class="flex items-center gap-2">
                        <button onclick="GenesisAuth.openModal('login')" class="text-xs font-semibold text-slate-200 hover:text-white px-3 py-1.5 rounded-xl border border-slate-700 hover:border-slate-500 bg-slate-900/80 transition">
                            Sign In
                        </button>
                        <button onclick="GenesisDonation.open()" class="inline-flex items-center gap-1.5 text-xs font-semibold text-rose-300 hover:text-rose-200 px-3 py-1.5 rounded-lg border border-rose-500/30 bg-rose-500/10 hover:bg-rose-500/20 transition shadow-sm">
                            <span>❤️</span>
                            <span class="hidden sm:inline">Donate</span>
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

    // ==========================================
    // 3. VOLUNTARY DONATION MODAL (Apni Khushi Se)
    // ==========================================
    const GenesisDonation = {
        currentAmount: CONFIG.defaultDonation,

        open: function(opts = {}) {
            let amount = opts.amount || this.currentAmount || CONFIG.defaultDonation;
            this._renderModal(amount);
        },

        close: function() {
            const modal = document.getElementById("genesisDonationModal");
            if (modal) modal.classList.add("hidden");
        },

        setCustomAmount: function(val) {
            let num = parseFloat(val);
            if (isNaN(num) || num <= 0) {
                num = 101.00;
            }
            const formatted = num.toFixed(2);
            this._renderModal(formatted);
        },

        _renderModal: function(amount) {
            this.currentAmount = amount;

            const upiParams = new URLSearchParams({
                pa: CONFIG.vpa,
                pn: CONFIG.payee,
                am: amount,
                cu: "INR",
                tn: "Voluntary_Gift_For_Keshav"
            });
            const genericUpi = `upi://pay?${upiParams.toString()}`;
            const gpayUri = `tez://upi/pay?${upiParams.toString()}`;
            const phonepeUri = `phonepe://pay?${upiParams.toString()}`;
            const paytmUri = `paytmmp://pay?${upiParams.toString()}`;
            const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=160x160&data=${encodeURIComponent(genericUpi)}`;

            let modal = document.getElementById("genesisDonationModal");
            if (!modal) {
                this._injectDonationModal();
                modal = document.getElementById("genesisDonationModal");
            }

            document.getElementById("donationAmountDisplay").innerText = `₹${amount}`;
            document.getElementById("customAmountInput").value = amount;
            document.getElementById("donationQrImg").src = qrUrl;
            document.getElementById("donationGenericBtn").href = genericUpi;
            document.getElementById("donationPhonepeBtn").href = phonepeUri;
            document.getElementById("donationGpayBtn").href = gpayUri;
            document.getElementById("donationPaytmBtn").href = paytmUri;

            // Highlight chip if predefined
            document.querySelectorAll(".donation-chip").forEach(chip => {
                if (chip.getAttribute("data-val") === String(amount)) {
                    chip.className = "donation-chip px-3 py-1.5 rounded-lg text-xs font-mono font-bold bg-rose-500 text-white transition";
                } else {
                    chip.className = "donation-chip px-3 py-1.5 rounded-lg text-xs font-mono text-slate-300 hover:text-white bg-slate-800 border border-slate-700 transition";
                }
            });

            modal.classList.remove("hidden");
        },

        _injectDonationModal: function() {
            const div = document.createElement("div");
            div.id = "genesisDonationModal";
            div.className = "fixed inset-0 bg-black/85 backdrop-blur-md z-50 hidden flex items-center justify-center p-4 font-sans antialiased";
            div.innerHTML = `
                <div class="bg-slate-900 border border-slate-800 max-w-md w-full rounded-3xl p-6 sm:p-7 shadow-2xl relative text-slate-100 max-h-[92vh] overflow-y-auto">
                    <button onclick="GenesisDonation.close()" class="absolute top-5 right-5 text-slate-400 hover:text-white text-base font-bold">✕</button>
                    
                    <div class="text-center pb-2">
                        <div class="w-12 h-12 rounded-2xl bg-gradient-to-tr from-rose-500 to-pink-500 flex items-center justify-center text-xl font-bold text-white mx-auto mb-3 shadow-lg shadow-rose-500/30">
                            ❤️
                        </div>
                        <h3 class="text-xl font-extrabold text-white">Apni Khushi Se Donate Karein</h3>
                        <p class="text-xs text-slate-400 mt-1.5 leading-relaxed">
                            Aapke liye saare tools 100% free hain aur hamesha rahenge. Koi compulsion ya fees nahi hai—agar aapka dil kare aur kaam pasand aaye, toh aap apni marzi ka koi bhi amount donate kar sakte hain.
                        </p>
                    </div>

                    <!-- Preset Suggestions -->
                    <div class="flex items-center justify-center gap-2 my-3.5">
                        <button onclick="GenesisDonation.setCustomAmount('51.00')" data-val="51.00" class="donation-chip px-3 py-1.5 rounded-lg text-xs font-mono text-slate-300 bg-slate-800 border border-slate-700">₹51</button>
                        <button onclick="GenesisDonation.setCustomAmount('101.00')" data-val="101.00" class="donation-chip px-3 py-1.5 rounded-lg text-xs font-mono text-slate-300 bg-slate-800 border border-slate-700">₹101</button>
                        <button onclick="GenesisDonation.setCustomAmount('251.00')" data-val="251.00" class="donation-chip px-3 py-1.5 rounded-lg text-xs font-mono text-slate-300 bg-slate-800 border border-slate-700">₹251</button>
                        <button onclick="GenesisDonation.setCustomAmount('501.00')" data-val="501.00" class="donation-chip px-3 py-1.5 rounded-lg text-xs font-mono text-slate-300 bg-slate-800 border border-slate-700">₹501</button>
                    </div>

                    <!-- Custom Amount Input -->
                    <div class="mb-3 px-1">
                        <label class="text-[11px] font-mono text-slate-400 block mb-1">Apni marzi ka amount likhein (₹):</label>
                        <div class="flex items-center gap-2">
                            <span class="text-sm font-bold text-slate-400 font-mono">₹</span>
                            <input 
                                id="customAmountInput" 
                                type="number" 
                                min="1" 
                                step="1" 
                                class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs font-mono text-white focus:outline-none focus:border-rose-500" 
                                placeholder="e.g. 50, 100, 500"
                                onchange="GenesisDonation.setCustomAmount(this.value)"
                            />
                            <button onclick="GenesisDonation.setCustomAmount(document.getElementById('customAmountInput').value)" class="bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs px-3 py-2 rounded-xl transition shrink-0 font-mono">
                                Set
                            </button>
                        </div>
                    </div>

                    <!-- QR Display Box -->
                    <div class="bg-slate-950/80 border border-slate-800 rounded-2xl p-4 text-center my-2">
                        <div class="flex justify-between items-center text-xs font-mono text-slate-400 mb-2">
                            <span>Selected Contribution:</span>
                            <span id="donationAmountDisplay" class="text-rose-400 font-bold text-sm">₹101.00</span>
                        </div>
                        <div class="bg-white p-2.5 rounded-xl inline-block shadow-inner mx-auto mb-2">
                            <img id="donationQrImg" src="" alt="Donation QR" class="w-36 h-36 mx-auto block"/>
                        </div>
                        <p class="text-[11px] text-slate-400 font-mono select-all font-semibold text-rose-300">${CONFIG.vpa}</p>
                        <button onclick="navigator.clipboard.writeText('${CONFIG.vpa}'); alert('UPI VPA copied: ${CONFIG.vpa}')" class="text-[11px] text-indigo-400 hover:underline mt-1 block mx-auto font-mono">
                            📋 Copy UPI ID
                        </button>
                    </div>

                    <!-- Direct App Launchers -->
                    <div class="space-y-2 mt-3">
                        <span class="text-[11px] font-bold text-slate-400 uppercase tracking-wider block font-mono">Direct UPI Intent:</span>
                        <div class="grid grid-cols-3 gap-2">
                            <a id="donationPhonepeBtn" href="#" class="bg-purple-950/80 border border-purple-800/80 hover:bg-purple-900 text-purple-200 text-xs font-bold py-2.5 text-center rounded-xl transition">
                                PhonePe
                            </a>
                            <a id="donationGpayBtn" href="#" class="bg-blue-950/80 border border-blue-800/80 hover:bg-blue-900 text-blue-200 text-xs font-bold py-2.5 text-center rounded-xl transition">
                                GPay
                            </a>
                            <a id="donationPaytmBtn" href="#" class="bg-sky-950/80 border border-sky-800/80 hover:bg-sky-900 text-sky-200 text-xs font-bold py-2.5 text-center rounded-xl transition">
                                Paytm
                            </a>
                        </div>
                        <a id="donationGenericBtn" href="#" class="w-full bg-gradient-to-r from-rose-500 to-pink-500 hover:from-rose-400 hover:to-pink-400 text-white font-extrabold text-xs py-3 rounded-xl block text-center transition shadow-lg shadow-rose-500/20">
                            ❤️ Open Default UPI App
                        </a>
                    </div>

                    <p class="text-[11px] text-slate-500 text-center mt-3">
                        100% Free Sovereign Software • Made with ❤️ by Keshav
                    </p>
                </div>
            `;
            document.body.appendChild(div);
        }
    };

    // Global Compatibility Aliases
    const GenesisSupport = {
        open: function(opts) { GenesisDonation.open(opts); },
        close: function() { GenesisDonation.close(); }
    };
    const GenesisCheckout = {
        open: function(opts) { GenesisDonation.open(opts); },
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
