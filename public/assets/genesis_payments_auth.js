/**
 * GENESIS SOVEREIGN CORE & VOLUNTARY DEVELOPER SUPPORT v4.0
 * 100% Free & Open Client-Side Access.
 * Direct Voluntary Support VPA: keshavthakur07@ptyes (Payee: Keshav)
 * Zero Paywalls • Zero Artificial Restrictions • Pure Developer Love
 */

(function(window) {
    'use strict';

    const CONFIG = {
        vpa: "keshavthakur07@ptyes",
        payee: "Keshav",
        defaultTip: "100.00",
        rapidApiUrl: "https://rapidapi.com/keshavkumarthakur00007/api/csv-to-json-high-speed-mapper",
        githubUrl: "https://github.com/keshavs40344/ai-world-core"
    };

    // ==========================================
    // 1. SOVEREIGN AUTH & STATUS (All Features 100% Free)
    // ==========================================
    const GenesisAuth = {
        getCurrentUser: function() {
            try {
                const user = localStorage.getItem("genesis_auth_user");
                return user ? JSON.parse(user) : { email: "builder@genesis.io", tier: "SUPPORTER", licenseValid: true };
            } catch(e) {
                return { email: "builder@genesis.io", tier: "SUPPORTER", licenseValid: true };
            }
        },

        isLoggedIn: function() {
            return true;
        },

        hasProAccess: function() {
            // All tools are 100% free and unlocked forever
            return true;
        },

        login: function(email) {
            const cleanEmail = (email || "builder@genesis.io").trim().toLowerCase();
            const session = {
                email: cleanEmail,
                tier: "SUPPORTER",
                token: "gnx_" + Math.random().toString(36).substr(2, 12),
                loginAt: new Date().toISOString()
            };
            localStorage.setItem("genesis_auth_user", JSON.stringify(session));
            this.updateNavbarAuth();
            return { success: true, user: session };
        },

        logout: function() {
            localStorage.removeItem("genesis_auth_user");
            this.updateNavbarAuth();
            window.location.reload();
        },

        updateNavbarAuth: function() {
            const authContainer = document.getElementById("genesisAuthWidget");
            if (!authContainer) return;
            authContainer.innerHTML = `
                <button onclick="GenesisSupport.open()" class="inline-flex items-center gap-1.5 text-xs font-semibold text-amber-300 hover:text-amber-200 px-3 py-1.5 rounded-lg border border-amber-500/30 bg-amber-500/10 hover:bg-amber-500/20 transition shadow-sm">
                    <span>☕</span>
                    <span>Support Developer</span>
                </button>
            `;
        }
    };

    // ==========================================
    // 2. VOLUNTARY DEVELOPER SUPPORT MODAL
    // ==========================================
    const GenesisSupport = {
        open: function(opts = {}) {
            let amount = opts.amount || CONFIG.defaultTip;
            this._renderModal(amount);
        },

        close: function() {
            const modal = document.getElementById("genesisSupportModal");
            if (modal) modal.classList.add("hidden");
        },

        setAmount: function(amount) {
            this._renderModal(amount);
        },

        _renderModal: function(amount) {
            const upiParams = new URLSearchParams({
                pa: CONFIG.vpa,
                pn: CONFIG.payee,
                am: amount,
                cu: "INR",
                tn: "Support_Independent_Developer_Keshav"
            });
            const genericUpi = `upi://pay?${upiParams.toString()}`;
            const gpayUri = `tez://upi/pay?${upiParams.toString()}`;
            const phonepeUri = `phonepe://pay?${upiParams.toString()}`;
            const paytmUri = `paytmmp://pay?${upiParams.toString()}`;
            const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=160x160&data=${encodeURIComponent(genericUpi)}`;

            let modal = document.getElementById("genesisSupportModal");
            if (!modal) {
                this._injectSupportModal();
                modal = document.getElementById("genesisSupportModal");
            }

            document.getElementById("tipAmountDisplay").innerText = `₹${amount}`;
            document.getElementById("supportQrImg").src = qrUrl;
            document.getElementById("tipGenericBtn").href = genericUpi;
            document.getElementById("tipPhonepeBtn").href = phonepeUri;
            document.getElementById("tipGpayBtn").href = gpayUri;
            document.getElementById("tipPaytmBtn").href = paytmUri;

            // Highlight selected tip pill
            document.querySelectorAll(".tip-pill").forEach(pill => {
                if (pill.getAttribute("data-amount") === String(amount)) {
                    pill.className = "tip-pill px-3 py-1.5 rounded-lg text-xs font-mono font-bold bg-amber-500 text-slate-950 transition";
                } else {
                    pill.className = "tip-pill px-3 py-1.5 rounded-lg text-xs font-mono text-slate-300 hover:text-white bg-slate-800 border border-slate-700 transition";
                }
            });

            modal.classList.remove("hidden");
        },

        _injectSupportModal: function() {
            const div = document.createElement("div");
            div.id = "genesisSupportModal";
            div.className = "fixed inset-0 bg-black/85 backdrop-blur-md z-50 hidden flex items-center justify-center p-4 font-sans antialiased";
            div.innerHTML = `
                <div class="bg-slate-900 border border-slate-800 max-w-md w-full rounded-3xl p-6 sm:p-7 shadow-2xl relative text-slate-100 max-h-[92vh] overflow-y-auto">
                    <button onclick="GenesisSupport.close()" class="absolute top-5 right-5 text-slate-400 hover:text-white text-base font-bold">✕</button>
                    
                    <div class="text-center pb-3">
                        <div class="w-12 h-12 rounded-2xl bg-gradient-to-tr from-amber-500 to-yellow-400 flex items-center justify-center text-xl font-bold text-slate-950 mx-auto mb-3 shadow-lg shadow-amber-500/30">
                            ☕
                        </div>
                        <h3 class="text-xl font-extrabold text-white">Support The Developer</h3>
                        <p class="text-xs text-slate-400 mt-1 leading-relaxed">
                            All 50+ tools are 100% free and open for everyone. If this saved your time, consider buying <strong>Keshav</strong> a coffee!
                        </p>
                    </div>

                    <!-- Tip Selector Pills -->
                    <div class="flex items-center justify-center gap-2 my-4">
                        <button onclick="GenesisSupport.setAmount('50.00')" data-amount="50.00" class="tip-pill px-3 py-1.5 rounded-lg text-xs font-mono text-slate-300 bg-slate-800 border border-slate-700">₹50 (Chai)</button>
                        <button onclick="GenesisSupport.setAmount('100.00')" data-amount="100.00" class="tip-pill px-3 py-1.5 rounded-lg text-xs font-mono text-slate-300 bg-slate-800 border border-slate-700">₹100 (Coffee)</button>
                        <button onclick="GenesisSupport.setAmount('299.00')" data-amount="299.00" class="tip-pill px-3 py-1.5 rounded-lg text-xs font-mono text-slate-300 bg-slate-800 border border-slate-700">₹299 (Lunch)</button>
                        <button onclick="GenesisSupport.setAmount('499.00')" data-amount="499.00" class="tip-pill px-3 py-1.5 rounded-lg text-xs font-mono text-slate-300 bg-slate-800 border border-slate-700">₹499 (Sponsor)</button>
                    </div>

                    <!-- QR Display -->
                    <div class="bg-slate-950/80 border border-slate-800 rounded-2xl p-4 text-center my-3">
                        <div class="flex justify-between items-center text-xs font-mono text-slate-400 mb-2">
                            <span>Contribution:</span>
                            <span id="tipAmountDisplay" class="text-emerald-400 font-bold text-sm">₹100.00</span>
                        </div>
                        <div class="bg-white p-2.5 rounded-xl inline-block shadow-inner mx-auto mb-2">
                            <img id="supportQrImg" src="" alt="Support QR" class="w-36 h-36 mx-auto block"/>
                        </div>
                        <p class="text-[11px] text-slate-400 font-mono select-all font-semibold text-emerald-400">${CONFIG.vpa}</p>
                        <button onclick="navigator.clipboard.writeText('${CONFIG.vpa}'); alert('UPI VPA copied: ${CONFIG.vpa}')" class="text-[11px] text-indigo-400 hover:underline mt-1 block mx-auto font-mono">
                            📋 Copy UPI VPA
                        </button>
                    </div>

                    <!-- Quick App Launchers -->
                    <div class="space-y-2 mt-4">
                        <span class="text-[11px] font-bold text-slate-400 uppercase tracking-wider block font-mono">One-Tap Direct Tip:</span>
                        <div class="grid grid-cols-3 gap-2">
                            <a id="tipPhonepeBtn" href="#" class="bg-purple-950/80 border border-purple-800/80 hover:bg-purple-900 text-purple-200 text-xs font-bold py-2.5 text-center rounded-xl transition">
                                PhonePe
                            </a>
                            <a id="tipGpayBtn" href="#" class="bg-blue-950/80 border border-blue-800/80 hover:bg-blue-900 text-blue-200 text-xs font-bold py-2.5 text-center rounded-xl transition">
                                GPay
                            </a>
                            <a id="tipPaytmBtn" href="#" class="bg-sky-950/80 border border-sky-800/80 hover:bg-sky-900 text-sky-200 text-xs font-bold py-2.5 text-center rounded-xl transition">
                                Paytm
                            </a>
                        </div>
                        <a id="tipGenericBtn" href="#" class="w-full bg-amber-500 hover:bg-amber-400 text-slate-950 font-extrabold text-xs py-3 rounded-xl block text-center transition shadow-lg shadow-amber-500/20">
                            ⚡ Tip via any UPI App
                        </a>
                    </div>

                    <p class="text-[11px] text-slate-500 text-center mt-4">
                        Made with ❤️ by Keshav. 100% free, private &amp; open sovereign software.
                    </p>
                </div>
            `;
            document.body.appendChild(div);
        }
    };

    // Backward compatibility alias so existing calls never throw errors
    const GenesisCheckout = {
        open: function(opts = {}) {
            GenesisSupport.open(opts);
        },
        close: function() {
            GenesisSupport.close();
        },
        verifyUtrSubmission: function() {
            alert("All tools are 100% free and unlocked! Thank you for supporting!");
            GenesisSupport.close();
        }
    };

    // Auto-mount on DOM ready
    window.addEventListener("DOMContentLoaded", () => {
        GenesisAuth.updateNavbarAuth();
    });

    window.GenesisAuth = GenesisAuth;
    window.GenesisSupport = GenesisSupport;
    window.GenesisCheckout = GenesisCheckout;

})(window);
