//
//  SignUpView.swift
//  MatchMate
//

import SwiftUI

struct SignUpView: View {
    @Binding var path: NavigationPath
    @EnvironmentObject var appState: AppState
    @State private var email = ""
    @State private var password = ""
    @State private var confirmPassword = ""
    @State private var errorMessage: String?

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text("Create account")
                    .font(.title2)
                    .fontWeight(.bold)

                TextField("Email", text: $email)
                    .textContentType(.emailAddress)
                    .autocapitalization(.none)
                    .keyboardType(.emailAddress)
                    .textFieldStyle(.roundedBorder)

                SecureField("Password", text: $password)
                    .textContentType(.newPassword)
                    .textFieldStyle(.roundedBorder)

                SecureField("Confirm password", text: $confirmPassword)
                    .textContentType(.newPassword)
                    .textFieldStyle(.roundedBorder)

                if let err = errorMessage {
                    Text(err)
                        .font(.caption)
                        .foregroundColor(.red)
                }

                Button(action: submit) {
                    Text("Continue")
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
        .navigationTitle("Sign up")
        .navigationBarTitleDisplayMode(.inline)
    }

    private func submit() {
        errorMessage = nil
        guard !email.isEmpty, !password.isEmpty else {
            errorMessage = "Enter email and password."
            return
        }
        guard password == confirmPassword else {
            errorMessage = "Passwords don't match."
            return
        }
        guard password.count >= 6 else {
            errorMessage = "Password must be at least 6 characters."
            return
        }
        appState.setPendingSignUp(email: email, password: password)
        path.append(AuthStep.profileCreation)
    }
}

#Preview {
    NavigationStack {
        SignUpView(path: .constant(NavigationPath()))
            .environmentObject(AppState())
    }
}
