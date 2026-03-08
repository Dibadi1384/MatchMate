//
//  LoginView.swift
//  MatchMate
//

import SwiftUI

struct LoginView: View {
    @Binding var path: NavigationPath
    @EnvironmentObject var appState: AppState
    @State private var email = ""
    @State private var password = ""
    @State private var errorMessage: String?

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text("Welcome back")
                    .font(.title2)
                    .fontWeight(.bold)

                TextField("Email", text: $email)
                    .textContentType(.emailAddress)
                    .autocapitalization(.none)
                    .keyboardType(.emailAddress)
                    .textFieldStyle(.roundedBorder)

                SecureField("Password", text: $password)
                    .textContentType(.password)
                    .textFieldStyle(.roundedBorder)

                if let err = errorMessage {
                    Text(err)
                        .font(.caption)
                        .foregroundColor(.red)
                }

                Button(action: submit) {
                    Text("Login")
                        .fontWeight(.semibold)
                        .frame(maxWidth: .infinity)
                        .padding()
                        .background(Color.accentColor)
                        .foregroundColor(.white)
                        .clipShape(RoundedRectangle(cornerRadius: 12))
                }
                .padding(.top, 8)
            }
            .padding(24)
        }
        .navigationTitle("Login")
        .navigationBarTitleDisplayMode(.inline)
    }

    private func submit() {
        errorMessage = nil
        guard !email.isEmpty, !password.isEmpty else {
            errorMessage = "Enter email and password."
            return
        }
        appState.login(email: email, password: password)
        // ContentView will switch to HomeView when isLoggedIn becomes true
    }
}

#Preview {
    NavigationStack {
        LoginView(path: .constant(NavigationPath()))
            .environmentObject(AppState())
    }
}
