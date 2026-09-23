const state = { service: 'Frontal Installation', price: 450, deposit: 150, duration: 120, date: '25 September', dateLabel: 'Friday, 25 September 2026', time: '09:00', timezone: 'Africa/Johannesburg (SAST)', paidBooking: null, serviceId: null, serviceMap: {} };
const availability = { '25 September': ['11:00'], '26 September': ['10:00', '15:00'], '28 September': ['12:00'], '29 September': [] };
const services = { 'Frontal Installation': 120, 'Classic Lashes': 90, 'Hybrid Lashes': 105 };
const $ = selector => document.querySelector(selector);
const $$ = selector => document.querySelectorAll(selector);
function formatDuration(minutes) { return `${Math.floor(minutes / 60)} hr${minutes >= 120 ? 's' : ''}${minutes % 60 ? ` ${minutes % 60} min` : ''}`; }
function setStep(step) { $$('.booking-step').forEach(item => item.classList.remove('active-step')); $(`#step${step === 1 ? 'One' : step === 2 ? 'Two' : 'Three'}`).classList.add('active-step'); $$('.step-indicator span').forEach((item, index) => item.classList.toggle('active', index < step)); if (step === 2) renderSlots(); }
function updateSummary() { $('#summaryService').textContent = state.service; $('#summaryTotal').textContent = `R${state.price}`; $('#summaryDeposit').textContent = `R${state.deposit}`; $('#summaryTime').textContent = state.time; }
function showToast(message) { const toast = $('#toast'); toast.textContent = message; toast.classList.add('show'); setTimeout(() => toast.classList.remove('show'), 3000); }
function formatWhatsAppNumber(phone) { const digits = phone.replace(/\D/g, ''); if (digits.startsWith('0')) return `27${digits.slice(1)}`; if (digits.startsWith('27')) return digits; return digits; }
function timeToMinutes(time) { const [hours, minutes] = time.split(':').map(Number); return hours * 60 + minutes; }
function minutesToTime(minutes) { return `${String(Math.floor(minutes / 60)).padStart(2, '0')}:${String(minutes % 60).padStart(2, '0')}`; }
function parseBookingDate(dateLabel) {
  const monthMap = { January: '01', February: '02', March: '03', April: '04', May: '05', June: '06', July: '07', August: '08', September: '09', October: '10', November: '11', December: '12' };
  const match = dateLabel.match(/(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})/i);
  if (!match) return null;

  const day = String(match[1]).padStart(2, '0');
  const month = monthMap[match[2].charAt(0).toUpperCase() + match[2].slice(1).toLowerCase()];
  const year = match[3];
  return `${year}-${month}-${day}`;
}
function resetBookingFlow() {
  $('#clientName').value = '';
  $('#clientPhone').value = '';
  $('#clientNote').value = '';
  $('#confirmation').classList.remove('show');
  $('#confirmation').classList.remove('cancelled');
  $('#cancelButton').disabled = false;
  $('#rescheduleButton').disabled = false;
  $$('.booking-step').forEach(item => item.style.display = '');
  setStep(1);
  state.time = '09:00';
  updateSummary();
  renderSlots();
}
function renderSlots() { const slots = $('#timeSlots'); const blocked = availability[state.date] || []; const opening = 8 * 60; const closing = 19 * 60; const step = 60; const lunchStart = 13 * 60; if (!document.querySelector('.hours-note')) { const note = document.createElement('div'); note.className = 'hours-note'; note.innerHTML = 'Open every day · <strong>08:00–19:00</strong>'; slots.parentElement.insertBefore(note, document.querySelector('.timezone-note')); } slots.innerHTML = ''; $('#selectedDateLabel').textContent = `${state.dateLabel} · ${formatDuration(state.duration)}`; $('#slotHint').textContent = `${formatDuration(state.duration)} appointment`; for (let start = opening; start + state.duration <= closing; start += step) { const time = minutesToTime(start); const overlapsLunch = start < lunchStart + 60 && start + state.duration > lunchStart; const isBooked = blocked.includes(time); const button = document.createElement('button'); button.className = `time${isBooked ? ' booked' : ''}${overlapsLunch ? ' lunch' : ''}${time === state.time && !isBooked && !overlapsLunch ? ' selected' : ''}`; button.disabled = isBooked || overlapsLunch; button.innerHTML = `${time}${isBooked ? '<small>Booked</small>' : overlapsLunch ? '<small>Lunch</small>' : ''}`; if (!button.disabled) button.addEventListener('click', () => { $$('.time').forEach(item => item.classList.remove('selected')); button.classList.add('selected'); state.time = time; updateSummary(); }); slots.appendChild(button); } if (!slots.querySelector('.time:not(:disabled)')) slots.innerHTML = '<p class="no-slots">No times fit this service on this date. Please choose another date.</p>'; }
const renderSlotsWithDuration = renderSlots;
renderSlots = () => {
  renderSlotsWithDuration();
  $('#selectedDateLabel').textContent = state.dateLabel;
  $('#slotHint').textContent = 'Select an available time';
  document.querySelector('.timezone-note')?.remove();
};
async function fetchBookings() {
  try {
    const response = await fetch('/api/appointments/');
    if (!response.ok) return [];
    const payload = await response.json();
    return Array.isArray(payload.appointments) ? payload.appointments : [];
  } catch (error) {
    return [];
  }
}

async function loadServices() {
  try {
    const response = await fetch('/api/services/');
    if (!response.ok) throw new Error('Services API unavailable');
    const payload = await response.json();
    state.serviceMap = {};
    (payload.services || []).forEach(service => { state.serviceMap[service.name] = service.id; });
    const defaultService = payload.services && payload.services[0] ? payload.services[0].name : state.service;
    state.service = defaultService;
    const matchedService = (payload.services || []).find(service => service.name === state.service);
    if (matchedService) {
      state.serviceId = matchedService.id;
      state.price = Number(matchedService.price);
      state.deposit = Number(matchedService.deposit_amount);
      state.duration = Number(matchedService.duration_minutes);
      updateSummary();
    }
  } catch (error) {
    state.serviceMap = { ...services };
    state.serviceId = null;
  }
}

async function renderAdmin() {
  const list = $('#appointmentList');
  const bookings = await fetchBookings();
  const count = bookings.length;
  $('#bookingCount').textContent = count;
  $('#todayCount').textContent = count;

  if (!count) {
    list.innerHTML = '<div class="empty-admin">No paid bookings yet.</div>';
    return;
  }

  list.innerHTML = bookings.map(booking => {
    const initials = (booking.client || 'A').split(' ').map(part => part[0]).join('').slice(0, 2).toUpperCase();
    return `<article class="appointment"><time>${booking.start_time || 'Booked'}<small>Confirmed</small></time><div class="appointment-person"><div class="avatar coral">${initials}</div><div><h4>${booking.client}</h4><p>${booking.service} · ${booking.date}</p><span class="wa">${booking.whatsapp || 'No note added'}</span></div></div><span class="paid">● Deposit paid</span></article>`;
  }).join('');
}
function showConfirmation(booking) {
  if (!booking || !booking.name) return;
  state.paidBooking = booking;
  $('#confirmedName').textContent = booking.name.split(' ')[0];
  const confirmationMessage = `Hi ${booking.name}, your ${booking.service} appointment is confirmed for ${booking.dateLabel} at ${booking.timeLabel}.`;
  $('#confirmationDetails').textContent = `${booking.service} is confirmed for ${booking.dateLabel} at ${booking.timeLabel}. Your dummy payment was successful. Send the confirmation by WhatsApp or SMS below.`;
  $('#whatsappConfirm').href = `https://wa.me/${formatWhatsAppNumber(booking.whatsapp)}?text=${encodeURIComponent(confirmationMessage)}`;
  $('#smsConfirm').href = `sms:${booking.whatsapp}?body=${encodeURIComponent(confirmationMessage)}`;
  $$('.booking-step').forEach(item => item.style.display = 'none');
  $('#confirmation').classList.add('show');
}
const removedServiceChoice = document.querySelector('.choice[data-service="HD Lace Installation"]');
if (removedServiceChoice) removedServiceChoice.remove();
$$('.choice small').forEach(item => { item.textContent = item.textContent.replace(/^.*?·\s*/, ''); });
const defaultServiceChoice = document.querySelector('.choice[data-service="Frontal Installation"]');
if (defaultServiceChoice) defaultServiceChoice.classList.add('selected');
$$('.choice').forEach(choice => choice.addEventListener('click', () => { $$('.choice').forEach(item => item.classList.remove('selected')); choice.classList.add('selected'); state.service = choice.dataset.service; state.price = Number(choice.dataset.price); state.deposit = Number(choice.dataset.deposit); state.duration = services[state.service]; state.serviceId = state.serviceMap[state.service] || null; updateSummary(); }));
$$('.date').forEach(date => date.addEventListener('click', () => { $$('.date').forEach(item => item.classList.remove('selected')); date.classList.add('selected'); state.date = date.dataset.date; state.dateLabel = date.dataset.label; state.time = '09:00'; renderSlots(); }));
$$('.next-step').forEach(button => button.addEventListener('click', () => setStep(Number(button.dataset.next))));
$$('.back-step').forEach(button => button.addEventListener('click', () => setStep(Number(button.dataset.back))));
$('#timezoneSelect').addEventListener('change', event => { state.timezone = event.target.value; $('.timezone-note strong').textContent = state.timezone; showToast(`Times shown in ${state.timezone}.`); });
$('#payButton').addEventListener('click', async () => {
  const name = $('#clientName').value.trim();
  const phone = $('#clientPhone').value.trim();
  if (!name || !phone) {
    showToast('Add your name and WhatsApp number first.');
    return;
  }

  const bookingDate = parseBookingDate(state.dateLabel);
  const payload = {
    service_id: state.serviceId || state.serviceMap[state.service] || null,
    date: bookingDate,
    start_time: state.time,
    end_time: minutesToTime(timeToMinutes(state.time) + state.duration),
    name,
    whatsapp: phone,
    note: $('#clientNote').value.trim(),
    timezone: state.timezone,
    deposit_paid: false,
    status: 'PENDING',
  };

  if (!payload.service_id) {
    const runningStaticTest = window.location.port === '5500' || window.location.protocol === 'file:';
    if (!runningStaticTest) {
      showToast('A valid service could not be loaded.');
      return;
    }
  }

  const testPaymentUrl = `payment.html?amount=${encodeURIComponent(state.deposit)}&service=${encodeURIComponent(state.service)}&name=${encodeURIComponent(name)}`;
  const runningStaticTest = window.location.port === '5500' || window.location.protocol === 'file:';
  localStorage.setItem('sphelelePendingBooking', JSON.stringify({
    ...payload,
    service: state.service,
    price: state.price,
    deposit: state.deposit,
    dateLabel: state.dateLabel,
    timeLabel: state.time,
  }));

  if (runningStaticTest) {
    window.location.href = testPaymentUrl;
    return;
  }

  try {
    const response = await fetch('/api/appointments/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (response.ok || response.status === 202) {
      const data = await response.json();
      const pendingBooking = JSON.parse(localStorage.getItem('sphelelePendingBooking') || '{}');
      pendingBooking.appointment_id = data.appointment_id || null;
      localStorage.setItem('sphelelePendingBooking', JSON.stringify(pendingBooking));
    } else if (!runningStaticTest) {
      const data = await response.json().catch(() => ({}));
      showToast(data.error || 'Booking could not be started.');
      return;
    }
    window.location.href = testPaymentUrl;
  } catch (error) {
    // The static test server has no API, so continue into the local payment simulator.
    window.location.href = testPaymentUrl;
  }
});
$('#rescheduleButton').addEventListener('click', () => { $('#confirmation').classList.remove('show'); $$('.booking-step').forEach(item => item.style.display = ''); setStep(2); renderSlots(); showToast('Only available slots are shown.'); });
$('#cancelButton').addEventListener('click', () => {
  state.paidBooking = null;
  renderAdmin();
  $('#confirmationDetails').textContent = 'This booking has been cancelled. Any deposit refund is handled according to the studio policy.';
  $('#confirmation').classList.add('cancelled');
  $('#cancelButton').disabled = true;
  $('#rescheduleButton').disabled = true;
  setTimeout(() => resetBookingFlow(), 1200);
  showToast('Booking cancelled.');
});
$('#blockTime').addEventListener('click', () => $('#blockModal').classList.add('show')); $('.close-modal').addEventListener('click', () => $('#blockModal').classList.remove('show')); $('#saveBlock').addEventListener('click', () => { $('#blockModal').classList.remove('show'); showToast('Time blocked.'); }); $('#blockModal').addEventListener('click', event => { if (event.target.id === 'blockModal') $('#blockModal').classList.remove('show'); });
updateSummary(); renderSlots(); loadServices().then(() => renderAdmin());
['sphelelePendingBooking', 'spheleleConfirmedBooking'].forEach(key => {
  const booking = JSON.parse(localStorage.getItem(key) || 'null');
  if (booking && (booking.service === 'HD Lace Installation' || booking.duration === 150)) localStorage.removeItem(key);
});
const confirmedBooking = JSON.parse(localStorage.getItem('spheleleConfirmedBooking') || 'null');
if (new URLSearchParams(window.location.search).get('payment') === 'success') showConfirmation(confirmedBooking);
