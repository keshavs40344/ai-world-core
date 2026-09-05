/**
 * GENESIS SOVEREIGN PATRONAGE & VOLUNTARY DONATION ENGINE v5.0
 * 100% Free, Public & Open-Source Sovereign Software.
 * Direct Voluntary Patronage VPA: keshavthakur07@ptyes (Payee: Keshav)
 * No Paywalls • No Demands • Pure Voluntary Appreciation
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
    // 1. SOVEREIGN PATRON ENGINE
    // ==========================================
    const GenesisAuth = {
        getCurrentUser: function() {
            try {
                const user = localStorage.getItem("genesis_auth_user");
                return user ? JSON.parse(user) : { email: "community_member@genesis.io", tier: "COMMUNITY", licenseValid: true };
            } catch(e) {
                return { email: "community_member@genesis.io", tier: "COMMUNITY", licenseValid: true };
            }
        },

        isLoggedIn: function() {
            return true;
        },

        hasProAccess: function() {
            return true;
        },

        login: function(email) {
            const cleanEmail = (email || "patron@genesis.io").trim().toLowerCase();
            const session = {
                email: cleanEmail,
                tier: "PATRON",
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
                <button onclick="GenesisDonation.open()" class="inline-flex items-center gap-1.5 text-xs font-semibold text-rose-300 hover:text-rose-200 px-3 py-1.5 rounded-lg border border-rose-500/30 bg-rose-500/10 hover:bg-rose-500/20 transition shadow-sm">
                    <span>❤️</span>
                    <span>Donate (Khushi Se)</span>
                </button>
            `;
        }
    };

    // ==========================================
    // 2. VOLUNTARY DONATION MODAL (Apni Marzi Se)
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
