/* Sidebar toggle */
(function () {
  var toggle = document.getElementById('sidebarToggle');
  var wrapper = document.getElementById('wrapper');
  if (!toggle || !wrapper) return;

  toggle.addEventListener('click', function () {
    if (window.innerWidth <= 768) {
      wrapper.classList.toggle('sidebar-open');
    } else {
      wrapper.classList.toggle('sidebar-collapsed');
    }
  });

  /* Close sidebar on mobile when clicking outside */
  document.addEventListener('click', function (e) {
    if (window.innerWidth <= 768 &&
        wrapper.classList.contains('sidebar-open') &&
        !e.target.closest('#sidebar') &&
        !e.target.closest('#sidebarToggle')) {
      wrapper.classList.remove('sidebar-open');
    }
  });

  /* Auto-dismiss alerts after 5 seconds */
  setTimeout(function () {
    var alerts = document.querySelectorAll('.alert.alert-success, .alert.alert-info');
    alerts.forEach(function (el) {
      var bsAlert = bootstrap.Alert.getOrCreateInstance(el);
      bsAlert.close();
    });
  }, 5000);
})();
