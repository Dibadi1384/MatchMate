//
//  ChatDetailView.swift
//  MatchMate
//

import SwiftUI

struct ChatDetailView: View {
    let chatId: String
    @Binding var path: NavigationPath
    @EnvironmentObject var appState: AppState
    @State private var inputText = ""

    private var chat: Chat? {
        appState.chats.first { $0.id == chatId }
    }

    private var messages: [Message] {
        appState.messages[chatId] ?? []
    }

    private var otherUserId: String? {
        chat?.participantIds.first { $0 != appState.currentUser?.id }
    }

    private var otherUser: User? {
        guard let id = otherUserId else { return nil }
        return appState.users.first { $0.id == id }
    }

    var body: some View {
        VStack(spacing: 0) {
            ScrollViewReader { proxy in
                ScrollView {
                    LazyVStack(alignment: .leading, spacing: 8) {
                        ForEach(messages) { msg in
                            MessageBubble(message: msg, isFromMe: msg.senderId == appState.currentUser?.id)
                        }
                    }
                    .padding(16)
                }
                .onChange(of: messages.count) { _ in
                    if let last = messages.last {
                        withAnimation {
                            proxy.scrollTo(last.id, anchor: .bottom)
                        }
                    }
                }
            }

            HStack(spacing: 12) {
                TextField("Message", text: $inputText, axis: .vertical)
                    .textFieldStyle(.roundedBorder)
                    .lineLimit(1...4)

                Button(action: send) {
                    Image(systemName: "arrow.up.circle.fill")
                        .font(.system(size: 36))
                        .foregroundColor(inputText.isEmpty ? .gray : .accentColor)
                }
                .disabled(inputText.isEmpty)
            }
            .padding(12)
            .background(Color(.systemBackground))
        }
        .navigationTitle(otherUser?.email ?? "Chat")
        .navigationBarTitleDisplayMode(.inline)
    }

    private func send() {
        let text = inputText.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !text.isEmpty else { return }
        appState.sendMessage(chatId: chatId, text: text)
        inputText = ""
    }
}

struct MessageBubble: View {
    let message: Message
    let isFromMe: Bool

    var body: some View {
        HStack {
            if isFromMe { Spacer(minLength: 60) }
            Text(message.text)
                .padding(.horizontal, 14)
                .padding(.vertical, 10)
                .background(isFromMe ? Color.accentColor : Color(.systemGray5))
                .foregroundColor(isFromMe ? .white : .primary)
                .clipShape(RoundedRectangle(cornerRadius: 16))
            if !isFromMe { Spacer(minLength: 60) }
        }
    }
}

#Preview {
    NavigationStack {
        ChatDetailView(chatId: "c1", path: .constant(NavigationPath()))
            .environmentObject(AppState())
    }
}
