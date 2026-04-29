const SchoolUtils = {
    popupTimeout: null,
    showPopup: function(message, type) {
        const el = document.getElementById('popup-message');
        if (!el) return;
        el.innerText = message;
        el.style.display = 'block';

        if (type === 'success') {
            el.style.backgroundColor = '#d4edda';
            el.style.color = '#155724';
            el.style.border = '1px solid #c3e6cb';
        } else {
            el.style.backgroundColor = '#f8d7da';
            el.style.color = '#721c24';
            el.style.border = '1px solid #f5c6cb';
        }

        if (this.popupTimeout) clearTimeout(this.popupTimeout);
        this.popupTimeout = setTimeout(() => {
            el.style.display = 'none';
        }, 3000);
    },
    calculateAge: function(dobString) {
        if (!dobString) return "";
        const today = new Date();
        const birthDate = new Date(dobString);
        let age = today.getFullYear() - birthDate.getFullYear();
        const m = today.getMonth() - birthDate.getMonth();
        if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
            age--;
        }
        return age >= 0 ? age : 0;
    }
};
