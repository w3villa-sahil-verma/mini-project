import { MailCheck, ExternalLink } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"

interface RegistrationLinkSentDialogProps {
  open?: boolean
  onOpenChange?: (open: boolean) => void
  /** The email address the registration link was sent to. */
  email?: string
}

export function RegistrationLinkSentDialog({
  open = false,
  onOpenChange,
  email,
}: RegistrationLinkSentDialogProps) {
  // Opens Gmail with the account that matches the given email, when signed in.
  const gmailUrl = email && `https://mail.google.com/mail/?authuser=${encodeURIComponent(email)}`

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader className="items-center text-center sm:text-center">
          <div className="mb-2 flex size-12 items-center justify-center rounded-full bg-primary/10">
            <MailCheck className="size-6 text-primary" aria-hidden="true" />
          </div>
          <DialogTitle>Check your email</DialogTitle>
          <DialogDescription>
            We sent a registration link to{" "}
            <span className="font-medium text-foreground">{email}</span>.
          </DialogDescription>
        </DialogHeader>

        <DialogFooter className="sm:justify-center">
          <Button variant="outline" onClick={() => onOpenChange?.(false)}>
            Close
          </Button>
          <Button >
            <a href={gmailUrl} target="_blank" rel="noopener noreferrer" className="flex flex-nowrap gap-1">
              <ExternalLink aria-hidden="true" />
              Open Gmail
            </a>
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}