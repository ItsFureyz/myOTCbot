welcome-message =
    <b>Welcome to the bot</b>

    💼 Buy and sell anything – safely!
    From Telegram gifts and NFTs to tokens and fiat – deals are easy and risk-free.

    🔹 Convenient wallet management
    🔹 Referral system

    🛡 <b>Our TG channel:</b> https://t.me/otcgifttg/71034/71035
    📞 <b>Support:</b> /support

    Select the desired section below:

language-select =
    🌍 Choose your language / Выберите язык:

add-wallet-ton-exists =
    💼 <b>Your current wallet</b>: <code>{ $wallet }</code>

    Send a new wallet address to update it or press the button below to return to the menu.

add-wallet-ton-not-exists =
    🔑 <b>Add your TON wallet:</b>

    Please send your wallet address.

referral-link-text =
    🔗 <b>Your referral link:</b>

    <code>https://t.me/{ $bot_username }?start=ref={ $user_wallet} </code>

    👥 <b>Referral count:</b> { $referral_count }
    💰 <b>Referral earnings:</b> { $referral_earnings } TON
    40% of bot fees

add-wallet-card-exists =
    🔑 <b>Your current card:</b> <code>{ $wallet }</code>

    Send a new card to update or click the button below to return to the menu.

add-wallet-stars-not-exists =
    ⭐ <b>Add your Telegram username for receiving Stars:</b>

    Send your username in the format <code>@username</code>.

add-wallet-stars-exists =
    ⭐ <b>Current Stars username:</b> <code>@{ $wallet }</code>

    Send a new username to change it.


add-wallet-yoomoney-not-exists =
    💜 <b>Add your YooMoney wallet:</b>

    Send the wallet number (starts with 4100…).

add-wallet-yoomoney-exists =
    💜 <b>Current YooMoney wallet:</b> <code>{ $wallet }</code>

    Send a new wallet number to change it.
add-wallet-card-not-exists =
    💳 <b>Add your bank card:</b>

    Please send your card number (16 digits).

deals_create =
    💼 <b>Create a Deal</b>

    Enter the deal amount in { $format } <code>100.5</code>

deal_description =
    📝 <b>Provide details for this deal:</b>

    Example: <code>10 caps and Pepe...</code>

select_payment_method =
    💰 <b>Select payment method:</b>

sucessful_create_deal =
    ✅ <b>Deal successfully created!</b>

    💰 <b>Amount:</b> <code>{ $deal_amount } { $deal_amount_format }</code>
    📜 <b>Description:</b> <code>{ $deal_description }</code>

    { $payment_details }

    📌 <b>Seller requisites:</b> { $payment_details }
    📞 <b>Support:</b> /support

    📋 <b>Instructions for the seller:</b>
    1. The buyer transfers funds to the support requisites.
    2. Support verifies the payment and confirms it.
    3. After payment confirmation you transfer the goods to the buyer.
    4. The buyer confirms receipt of the goods in the bot.
    5. After confirmation of the goods transfer the funds are sent to your requisites.

    🔗 <b>Buyer Link:</b> https://t.me/{ $bot_username}?start={ $deal_id }

joined_to_deal =
    User @{ $username } ({ $user_id }) joined deal #{ $deal_id }
    • Successful deals: { $deals_count }

test_seller_confirmed =
    🛍 <b>Seller @{ $seller_username } confirmed item transfer</b> for deal #{ $deal_id }.

    Check the item and confirm the money transfer after the actual payment.

test_buyer_confirmed =
    💰 <b>Support has confirmed receipt of funds</b> for deal #{ $deal_id }.

    Buyer @{ $buyer_username } has transferred the funds. Now you need to transfer the goods to the buyer.

    After the actual transfer of the goods the buyer must confirm receipt in the bot.
    If the buyer does not confirm — send a screenshot of the transfer confirmation to this chat. Support will review it within 24–48 hours and complete the deal.

    Funds will be transferred to your requisites after confirmation of the goods transfer.

test_buyer_confirmed_member =
    💰 <b>Support has confirmed receipt of funds</b> for deal #{ $deal_id }.

    Please wait for the seller to transfer the goods.
    Confirm receipt <b>only after the actual transfer</b> of the goods.

confirm_goods_received = ✅ Confirm goods transfer

deal_transfer_waiting_seller =
    📦 <b>Goods transfer pending</b> for deal #{ $deal_id }.

    Transfer the goods to the buyer. After transfer the buyer will confirm receipt.
    If confirmation is not received — send a screenshot of the transfer to this chat.

deal_transfer_waiting_buyer =
    📦 <b>Wait for the goods transfer</b> for deal #{ $deal_id }.

    Confirm receipt only after the actual transfer of the goods.

screenshot_received =
    ✅ <b>Confirmation received.</b>

    Support will review your goods transfer confirmation within <b>24–48 hours</b>.

deal_info =
    💳 <b>Deal information</b> #{ $deal_id }

    👤 <b>You are the buyer</b> in this deal.
    📌 Seller: @{ $username } <b>({ $user_id })</b>
    • Successful deals: { $deals_count }

    • You are buying: { $deal_description }

    💰 <b>Amount to pay:</b> <code>{ $deal_amount }</code> { $currency }

    { $payment_details }

    📌 <b>Seller requisites:</b> { $payment_details }
    📞 <b>Support:</b> /support

    📋 <b>Instructions for the buyer:</b>
    1. Transfer funds to the support requisites (shown above / in the support message).
    2. Support verifies the payment and confirms it.
    3. After payment confirmation the seller transfers the goods to you.
    4. After receiving the goods confirm the transfer in the bot.
    5. After your confirmation the funds are sent to the seller’s requisites.

    📝 <b>Payment comment (memo):</b> <code>{ $deal_id }</code>

    ⚠️ <b>Please verify the data before payment. The comment (memo) is mandatory!</b>

    After payment wait for support confirmation.

deal_paid =
    ✅ <b>Payment confirmed for deal #{ $deal_id }</b>

    Description: { $deal_description }

    Send the gift to the buyer — @{ $deal_member_username }

    ⚠️ Send the gift only to the person listed here. If you send it to someone else there will be no refund. Be sure to record the transfer on video.

deal_paid_member =
    ✅ <b>Payment confirmed</b> for deal #{ $deal_id }

    Please confirm receipt of the gift after the seller sends it.

cancel_deal_text =
    ❌ Are you sure you want to cancel deal #{ $deal_id }?

    This action cannot be undone.

exit_deal_text =
    ❓ Are you sure you want to leave deal #{ $deal_id }?

    This will notify the seller and return the deal to its original state.

add-wallet = 🪙 Add/change wallet
ton-wallet = 💎 TON Wallet
card-wallet = 💳 Card
yoomoney-wallet = 💜 YooMoney wallet
stars-wallet = ⭐ Telegram Stars
create-deal = 📄 Create deal
referral-link = 🧷 Referral link
support = 📞 Support
back = 🔙 Back to menu
wallet_specified = ❌ First connect the required details via the menu. ❌ First connect a wallet via the menu.
incorrect_ton_wallet = ❌ Invalid TON wallet format. Please try again.
incorrect_stars_wallet = ❌ Invalid Telegram username. Use 5–32 characters: letters, digits and _.
incorrect_stars_amount = ❌ The number of Stars must be a positive integer.
incorrect_card_wallet = ❌ Invalid card format. MIR, Visa, Mastercard of Russian banks (Sber, T-Bank, VTB, Alfa, etc.) are supported. Please try again.
incorrect_yoomoney_wallet = ❌ Invalid YooMoney wallet format. The number must start with 4100 and contain 11–20 digits.
invalid_amount_format = ❌ Invalid amount format. Please try again.
successful_wallet = ✅ Wallet successfully added/changed!
tonkeeper_open = Open in Tonkeeper
exit_deal = ❌ Leave deal
cancel_deal = ❌ Cancel deal
invalid_deal_id = ❌ Invalid deal ID.
own_deal_unsupport = ❌ You cannot participate in your own deal.
already_buyer = ❌ This deal already has a buyer. You cannot join it.
select_payment_country = 💳 <b>Select currency for the card</b>
cancel_yes = ✅ Yes, Cancel
cancel_no = 🔙 No
deal_deleted = ✅ Deal successfully deleted
deal_cancel_delete = ❌ Action cancelled
exit_yes = ✅ Yes, leave
exit_no = 🔙 No
deal_exited = ✅ You have successfully left the deal
exited_deal = User @{ $exit_username } ({ $exit_id }) left deal #{ $deal_id }. The deal has been returned to its original state.
buyer = 👤 Buyer
allow_send_gift = 🎁 I confirm sending the gift
poluchil_gift = 🎁 I received the gift
deal_ended =
    ✅ <b>Deal #{ $deal_id } completed.</b>

    🤖 <b>Thank you for using our service.</b>
deal_ended_owner =
    ✅ <b>Deal #{ $deal_id } completed.</b>

    🤖 <b>Thank you for using our service.</b>

    💰 <b>Withdrawal to the specified details will be completed within 24–48 hours.</b>
deal_member_da = ✅ <b>The buyer has confirmed receipt of the gifts</b>

my_deals_title =
    📋 <b>Your deals</b>

    Select a deal to manage:

no_deals =
    You have no active deals.

deal_item_owner =
    #{ $deal_id } • { $amount } { $currency } • Seller • { $status }

deal_item_member =
    #{ $deal_id } • { $amount } { $currency } • Buyer • { $status }

continue_deal = ▶ Continue deal
delete_deal_btn = 🗑 Delete deal
leave_deal_btn = ❌ Leave deal
deal_already_active = ℹ️ You already have an active deal in progress. Please finish or leave it first.


support_prompt =
    📞 <b>Support</b>

    Please send your message to support in one message.
    We will reply within <b>24–48 hours</b>.

    To cancel, press the button below.

support_sent =
    ✅ <b>Your message has been sent to support.</b>

    Please wait for a reply within 24–48 hours.

support_cancel =
    ❌ Support request cancelled.
